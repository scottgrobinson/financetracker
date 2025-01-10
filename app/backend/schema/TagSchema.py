from ..extensions import db, ma
from ..model.Tag import Tag

class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag