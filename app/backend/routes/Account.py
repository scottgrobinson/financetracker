import time
from flask import Blueprint, jsonify, abort, request
from ..logger import logger
from ..extensions import db
from ..nordigen_processor import NordigenProcessor
from ..model.Account import Account
from ..model.Transaction import Transaction
from ..model.Tag import Tag
from ..model.Person import Person
from ..schema.AccountSchema import AccountSchema
from uuid import uuid4

AccountBlueprint = Blueprint('AccountBlueprint', __name__)

@AccountBlueprint.route('/', methods=['GET'])
def get_all_accounts():
    try:
        accounts = Account.query.with_entities(Account.id, Account.description, Account.balance, Account.eua_expired).all()
        return jsonify(AccountSchema(many=True).dump(accounts))
    except Exception as e:
        abort(500, description=str(e))

@AccountBlueprint.route('/<accountid>', methods=['GET'])
def get_account(accountid):
    try:
        account = Account.query.order_by(Transaction.datetime).get(accountid)
        if account is None:
            abort(404, description="Account not found")
        return jsonify(AccountSchema().dump(account))
    except Exception as e:
        abort(500, description=str(e))

@AccountBlueprint.route('/update', methods=['GET'])
def get_latest_accountbalances():
    try:
        NordigenProcessor().nordigen_update_balances()
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))

@AccountBlueprint.route('/<accountid>/<transactionid>/assignees', methods=['POST'])
def update_transaction_assignees(accountid, transactionid):
    # 1) Parse & validate JSON
    data = request.get_json(silent=True)
    if not data or 'assignees' not in data:
        abort(400, description="Payload must be JSON with an 'assignees' field")

    raw_list = data['assignees']
    if not isinstance(raw_list, list):
        abort(400, description="'assignees' must be a list")

    # 2) Normalize to list of ID strings
    new_ids = []
    for entry in raw_list:
        if isinstance(entry, dict):
            # expect { "id": "..." } shape
            pid = entry.get('id')
            if not pid:
                abort(400, description="Each assignee object must have an 'id'")
            new_ids.append(pid)
        else:
            # assume it's already an ID
            new_ids.append(entry)

    # 3) Load transaction
    tx = Transaction.query \
        .filter_by(id=transactionid, account_id=accountid) \
        .first()
    if tx is None:
        abort(404, description="Transaction not found")

    # 4) Fetch and validate all Person rows at once
    persons = Person.query.filter(Person.id.in_(new_ids)).all()
    found_ids = {p.id for p in persons}
    missing = set(new_ids) - found_ids
    if missing:
        abort(404, description=f"Person(s) not found: {', '.join(missing)}")

    # 5) Compute differences
    old_set = set(tx.assignees)
    new_set = set(persons)

    to_add    = new_set - old_set
    to_remove = old_set - new_set

    for p in to_add:
        tx.assignees.append(p)
    for p in to_remove:
        tx.assignees.remove(p)

    # 6) Commit with rollback on error
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"DB error: {e}")

    return jsonify({"success": True})

@AccountBlueprint.route('/<accountid>/<transactionid>/tag/<tag>', methods=['POST'])
def add_transaction_tag(accountid, transactionid, tag):
    try:
        tags = Tag.query.filter_by(account_id=accountid, transaction_id=transactionid)
        newtag = Tag()
        newtag.tag = tag
        newtag.transaction_id = transactionid
        newtag.account_id = accountid
        if newtag not in tags:
            db.session.add(newtag)
    except Exception as e:
        abort(500, description=str(e))
    else:
        db.session.commit()
        return jsonify({"success": True})

@AccountBlueprint.route('/<accountid>/<transactionid>/tag/<tag>', methods=['DELETE'])
def delete_transaction_tag(accountid, transactionid, tag):
    try:
        Tag.query.filter_by(account_id=accountid, transaction_id=transactionid, tag=tag).delete()
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))

@AccountBlueprint.route('/<accountid>/generatereneweuaurl', methods=['GET'])
def generate_renew_eua_url(accountid):
    account = Account.query.filter_by(id=accountid).first()

    init = NordigenProcessor().nordigen_client.initialize_session(
        institution_id=account.institution,
        redirect_uri='https://finances.home.poachinson.uk',
        reference_id=str(uuid4())
    )
    
    return jsonify({"success": True, "eua_expiry_url": init.link})
