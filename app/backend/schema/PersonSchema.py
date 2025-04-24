from ..extensions import db, ma
from ..model.Person import Person

class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person