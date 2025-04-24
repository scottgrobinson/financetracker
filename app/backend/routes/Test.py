from flask import Blueprint, jsonify, abort
from ..logger import logger
from ..extensions import db
from ..nordigen_processor import NordigenProcessor, NordigenProcessingError
from uuid import uuid4

TestBlueprint = Blueprint('TestBlueprint', __name__)

@TestBlueprint.route('/', methods=['GET'])
def test():
    #return NordigenProcessor().nordigen_client.institution.get_institutions(country='GB')
    init = NordigenProcessor().nordigen_client.initialize_session(
        institution_id='MONZO_MONZGB2L',
        redirect_uri='https://gocardless.com',
        reference_id=str(uuid4()),
    )

    redirect_url = init.link
    logger.info(init.requisition_id)
    return redirect_url
