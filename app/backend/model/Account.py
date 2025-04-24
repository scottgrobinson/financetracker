from ..extensions import db, ma

class Account(db.Model):
    id = db.Column(db.String(100), primary_key=True, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    balance_type = db.Column(db.String(100), nullable=False)
    eua_expired = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Float, nullable=False)

    transactions = db.relationship(
        'Transaction', backref='account', lazy=True, order_by='Transaction.datetime.desc()'
    )

    def __repr__(self):
        return f'<Account {self.id}>'