from ..extensions import db, ma
from ..model.Transaction import Transaction
from ..schema.TagSchema import TagSchema
from ..schema.PersonSchema import PersonSchema
from marshmallow import post_dump

class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        include_relationships = True

    tags = ma.Method("get_tag_list")
    assignees = ma.Nested(PersonSchema, many=True)

    def get_tag_list(self, obj):
        return [tag.tag for tag in obj.tags]

    # Register a method to invoke after serializing an object. The method receives the serialized object and returns the processed object.
    # ChatGPT told me to do this...
    @post_dump
    def hide_description(self, data, **kwargs):
        """
        After dumping the transaction to a dict,
        check if it's hidden. If so, override the description.
        """
        if data.get('hidden'):
            data['remittance_information'] = '** HIDDEN TRANSACTION **'
        return data