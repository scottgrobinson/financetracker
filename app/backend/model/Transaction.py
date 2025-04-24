from ..extensions import db, ma
from .TransactionPersonLink import TransactionPersonLink
from .Person import Person
from sqlalchemy import and_
from sqlalchemy.inspection import inspect

class Transaction(db.Model):
    id = db.Column(db.String(100), primary_key=True, nullable=False)
    account_id = db.Column(db.String(100), db.ForeignKey('account.id'), primary_key=True, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    creditor = db.Column(db.String(250), nullable=True)
    remittance_information = db.Column(db.String(250), nullable=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)

    tags = db.relationship(
        'Tag', backref='transaction', lazy=True
    )

    assignees = db.relationship(
        'Person',
        secondary=TransactionPersonLink,
        primaryjoin=and_(
            id == TransactionPersonLink.c.transaction_id,
            account_id == TransactionPersonLink.c.account_id
        ),
        secondaryjoin=Person.id == TransactionPersonLink.c.person_id,
    )

    def __repr__(self):
        return f'<Transaction (id={self.id}, account_id={self.account_id})>'

    def to_dict(self):
        # auto-serialize all normal columns
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        # format date
        data['datetime'] = self.datetime.isoformat()

        # add tags as a list of strings
        data['tags'] = [tag.tag for tag in self.tags]

        # add assignees as list of dicts (id + name)
        data['assignees'] = [
            {'id': person.id, 'name': person.name}
            for person in self.assignees
        ]

        return data