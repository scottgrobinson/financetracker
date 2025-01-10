from ..extensions import db, ma
from ..model.Transaction import Transaction
from ..schema.TagSchema import TagSchema

class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        include_relationships = True

    tags = ma.Method("get_tag_list")

    def get_tag_list(self, obj):
        return [tag.tag for tag in obj.tags]