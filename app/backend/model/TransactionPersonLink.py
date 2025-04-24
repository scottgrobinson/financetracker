from ..extensions import db, ma

TransactionPersonLink = db.Table(
    'transaction_person_link',
    db.Column('transaction_id', db.String(100), db.ForeignKey('transaction.id'), primary_key=True),
    db.Column('account_id', db.String(100), db.ForeignKey('account.id'), primary_key=True),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'), primary_key=True),
)
