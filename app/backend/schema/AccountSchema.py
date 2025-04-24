from ..extensions import db, ma
from ..model.Account import Account
from ..schema.TransactionSchema import TransactionSchema

class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Account
        include_relationships = True

    # ChatGPT told me to do this...
    # Something to do with the @post_dump function in TransactionSchema.py
    #transactions = ma.Nested(TransactionSchema, many=True)
    transactions = ma.List(ma.Nested(TransactionSchema))
