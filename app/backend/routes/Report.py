from flask import Blueprint, abort, jsonify, request
from datetime import datetime
from sqlalchemy import func, case
from ..logger import logger
from ..model.Transaction import Transaction
from ..model.Tag import Tag
from ..model.TransactionPersonLink import TransactionPersonLink

ReportBlueprint = Blueprint('ReportBlueprint', __name__)

@ReportBlueprint.route('/run', methods=['POST'])
def run_report():
    try:
        data = request.get_json(silent=True)
        if not data:
            abort(400, description="Invalid JSON data")

        logger.info("Received report request with data: %s", data)

        # --- parse & validate dates ---
        start_str = data.get('startDate')
        end_str   = data.get('endDate')
        if not start_str or not end_str:
            abort(400, description="Both startDate and endDate are required")

        try:
            start = datetime.fromisoformat(start_str)
            end   = datetime.fromisoformat(end_str)
        except ValueError:
            abort(400, description="Invalid date format. Use ISO 8601")

        if end < start:
            abort(400, description="endDate must be on or after startDate")

        # --- read joint-transactions flag (default true) ---
        include_joint = data.get('includeJointTransactions', True)
        if isinstance(include_joint, str):
            include_joint = include_joint.lower() == 'true'
        elif not isinstance(include_joint, bool):
            include_joint = True

        # --- normalize filter lists ---
        raw_accounts = data.get('accounts', [])
        accounts = []
        for a in raw_accounts:
            if isinstance(a, str):
                accounts.append(a)
            elif isinstance(a, dict):
                acc_id = a.get('id') or a.get('account_id')
                if isinstance(acc_id, str):
                    accounts.append(acc_id)

        raw_tags = data.get('tags', [])
        tags = []
        for t in raw_tags:
            if isinstance(t, str):
                tags.append(t)
            elif isinstance(t, dict):
                tag_str = t.get('tag')
                if isinstance(tag_str, str):
                    tags.append(tag_str)

        raw_assignees = data.get('assignees', [])
        assignees = []
        for p in raw_assignees:
            if isinstance(p, (int, str)):
                try:
                    assignees.append(int(p))
                except ValueError:
                    pass
            elif isinstance(p, dict):
                pid = p.get('id') or p.get('person_id')
                if isinstance(pid, (int, str)):
                    try:
                        assignees.append(int(pid))
                    except ValueError:
                        pass

        # --- build the base query ---
        q = Transaction.query.filter(
            Transaction.datetime >= start,
            Transaction.datetime <= end
        )

        # account filter
        if accounts:
            q = q.filter(Transaction.account_id.in_(accounts))

        # tag filter
        if tags:
            q = (
                q
                .join(Tag, Tag.transaction_id == Transaction.id)
                .filter(Tag.tag.in_(tags))
            )

        # assignee filter with joint-transactions support
        if assignees:
            # join the person link table
            table = TransactionPersonLink
            q = q.join(table, table.c.transaction_id == Transaction.id)

            if include_joint:
                # include any transaction with at least one matching assignee
                q = q.filter(table.c.person_id.in_(assignees))
            else:
                # only transactions with exactly one assignee and it must match
                q = (
                    q
                    .group_by(Transaction.id)
                    .having(
                        func.count(table.c.person_id) == 1,
                        func.count(case((table.c.person_id.in_(assignees), 1))) == 1
                    )
                )

        # fetch distinct results
        transactions = q.distinct().all()

        # --- serialize & return ---
        result = [t.to_dict() for t in transactions]
        return jsonify({"success": True, "transactions": result}), 200

    except Exception as e:
        logger.exception("Error running report")
        abort(500, description=str(e))
