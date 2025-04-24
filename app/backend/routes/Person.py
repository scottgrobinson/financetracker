import time
from flask import Blueprint, jsonify, abort
from ..logger import logger
from ..model.Person import Person
from ..schema.PersonSchema import PersonSchema
from uuid import uuid4

PersonBlueprint = Blueprint('PersonBlueprint', __name__)

@PersonBlueprint.route('/', methods=['GET'])
def get_all_persons():
    try:
        persons = Person.query.all()
        return jsonify(PersonSchema(many=True).dump(persons))
    except Exception as e:
        abort(500, description=str(e))