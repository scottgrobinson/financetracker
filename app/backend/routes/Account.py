import time
from flask import Blueprint, jsonify, abort
from ..logger import logger
from ..extensions import db
from ..nordigen_processor import NordigenProcessor
from ..model.Account import Account
from ..model.Transaction import Transaction
from ..model.Tag import Tag
from ..schema.AccountSchema import AccountSchema

AccountBlueprint = Blueprint('AccountBlueprint', __name__)

@AccountBlueprint.route('/', methods=['GET'])
def get_all_accounts():
    try:
        accounts = Account.query.with_entities(Account.id, Account.description, Account.balance).all()
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

@AccountBlueprint.route('/<accountid>/<transactionid>/tag/<tag>', methods=['DELETE'])
def delete_transaction_tag(accountid, transactionid, tag):
    try:
        Tag.query.filter_by(account_id=accountid, transaction_id=transactionid, tag=tag).delete()
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))