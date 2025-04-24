from flask import Blueprint, jsonify, abort, request
from ..logger import logger
from ..nordigen_processor import NordigenProcessor, NordigenProcessingError
from ..model.Transaction import Transaction
from ..schema.TransactionSchema import TransactionSchema

TransactionBlueprint = Blueprint('TransactionBlueprint', __name__)

@TransactionBlueprint.route('/update', methods=['GET'])
def get_latest_transactions():
    transactionfile = request.args.get('transactionfile')
    try:
        if transactionfile is not None:
            result = NordigenProcessor().nordigen_update_transactions(transactionfile)
        else:
            result = NordigenProcessor().nordigen_update_transactions()

        return jsonify({"success": True})
    except NordigenProcessingError as e:
        abort(400, description=str(e))
    except Exception as e:
        abort(500, description=str(e))
