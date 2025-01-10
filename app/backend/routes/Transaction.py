from flask import Blueprint, jsonify, abort, request
from ..logger import logger
from ..nordigen_processor import NordigenProcessor
from ..model.Transaction import Transaction
from ..schema.TransactionSchema import TransactionSchema

TransactionBlueprint = Blueprint('TransactionBlueprint', __name__)

@TransactionBlueprint.route('/update', methods=['GET'])
def get_latest_transactions():
    transactionfile = request.args.get('transactionfile')
    try:
        if transactionfile is not None:
            NordigenProcessor().nordigen_update_transactions(transactionfile)
        else:
            NordigenProcessor().nordigen_update_transactions()
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))