from applications import db
from datetime import datetime


class IncomeExpenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), default='income', nullable=False)
    category = db.Column(db.String(50), default='rent', nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f"{self.id}"