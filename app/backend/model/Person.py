from ..extensions import db, ma
from .TransactionPersonLink import TransactionPersonLink

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Person {self.id}>'