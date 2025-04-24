from flask import Blueprint, jsonify, abort, request
from ..logger import logger
from ..model.Tag import Tag
from ..extensions import db

TagBlueprint = Blueprint('TagBlueprint', __name__)

@TagBlueprint.route('/', methods=['GET'])
def get_all_tags():
    try:
        tag_names = [t[0] for t in
            db.session.query(Tag.tag).distinct().all()
        ]
        return jsonify(tag_names)
    except Exception as e:
        abort(500, description=str(e))