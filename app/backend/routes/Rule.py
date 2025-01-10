from flask import Blueprint, jsonify, abort, request
from ..logger import logger
from ..extensions import db
from ..model.Rule import Rule
from ..schema.RuleSchema import RuleSchema
from ..rule_engine import RuleEngine

RuleBlueprint = Blueprint('RuleBlueprint', __name__)

def saveRule(data, ruleid=None):
    if ruleid:
        rule = Rule.query.filter_by(id=ruleid).first()
    else:
        rule = Rule()
    rule.rule = data['rule']
    rule.action =  data['action']
    rule.action_value_1 = data['action_value_1']
    rule.action_value_2 = data['action_value_2']
    if not ruleid:
        db.session.add(rule)
    db.session.commit()

# List rules
@RuleBlueprint.route('/', methods=['GET'])
def get_all_rules():
    rules = Rule.query.all()
    return jsonify(RuleSchema(many=True).dump(rules))

# Run rules
@RuleBlueprint.route('/run', methods=['GET'])
def run_all_rules():
    try:
        RuleEngine().run_rules()
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))

# Add rule
@RuleBlueprint.route('/', methods=['POST'])
def add_rule():
    try:
        saveRule(request.json)
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))

# Save rule
@RuleBlueprint.route('/<ruleid>', methods=['PUT'])
def save_rule(ruleid):
    try:
        saveRule(request.json, ruleid)
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))

# Delete rule
@RuleBlueprint.route('/<ruleid>', methods=['DELETE'])
def delete_rule(ruleid):
    try:
        Rule.query.filter_by(id=ruleid).delete()
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        abort(500, description=str(e))