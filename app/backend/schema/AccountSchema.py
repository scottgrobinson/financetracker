from ..extensions import db, ma
from ..model.Account import Account
from ..schema.TransactionSchema import TransactionSchema

class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Account
        include_relationships = True

    transactions = ma.Nested(TransactionSchema, many=True)