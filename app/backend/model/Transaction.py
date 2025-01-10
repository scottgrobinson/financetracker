from ..extensions import db, ma

class Transaction(db.Model):
    id = db.Column(db.String(100), primary_key=True, nullable=False)
    account_id = db.Column(db.String(100), db.ForeignKey('account.id'), primary_key=True, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    creditor = db.Column(db.String(250), nullable=True)
    remittance_information = db.Column(db.String(250), nullable=False)
    
    tags = db.relationship(
        'Tag', backref='transaction', lazy=True
    )

    def __repr__(self):
        return f'<Transaction (id={self.id}, account_id={self.account_id})>'