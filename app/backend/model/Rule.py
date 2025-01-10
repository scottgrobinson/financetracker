from ..extensions import db, ma

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rule = db.Column(db.String(250), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    action_value_1 = db.Column(db.String(100), nullable=False)
    action_value_2 = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Rule {self.id}>'