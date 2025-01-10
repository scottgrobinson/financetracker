from ..extensions import db, ma
from ..model.Rule import Rule

class RuleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rule