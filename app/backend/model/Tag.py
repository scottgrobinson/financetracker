from ..extensions import db, ma

class Tag(db.Model):
    tag = db.Column(db.String(100), primary_key=True, nullable=False)
    transaction_id = db.Column(db.String(100), db.ForeignKey('transaction.id'), primary_key=True)
    account_id = db.Column(db.String(100), db.ForeignKey('account.id'), primary_key=True)

    # __eq__ and __hash__ allows me to do 
    # tags = Tag.query.all()
    # newtag = Tag()
    # ...
    # if newtag in tags:
    def __eq__(self, other):
        if not isinstance(other, Tag):
            return False
        return (
            self.tag == other.tag and
            self.transaction_id == other.transaction_id and
            self.account_id == other.account_id
        )

    def __hash__(self):
        return hash((self.tag, self.transaction_id, self.account_id))

    def __repr__(self):
        return f"<Tag (tag={self.tag}, transaction_id={self.transaction_id}, account_id={self.account_id})>"
