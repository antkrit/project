"""Payment cards database models"""
from uuid import uuid4
from datetime import datetime, timezone
from module import App
from module.server.models import BaseCard


db = App.db


class Card(BaseCard, db.Model):
    """Payment cards table"""
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True, unique=True)
    amount = db.Column(db.Integer, nullable=False, server_default='0')
    code = db.Column(db.String(64), nullable=False, index=True, unique=True, server_default='000000')

    def __repr__(self) -> str:
        """Returns representative string that displays code and amount of the card"""
        return 'Card #{0}: {1}. Code: {2}'.format(self.uuid, self.amount, self.code)


class UsedCard(BaseCard, db.Model):
    """Used payment cards table"""
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True, unique=True)
    amount = db.Column(db.Integer, nullable=False, server_default='0')
    code = db.Column(db.String(64), nullable=False, index=True, unique=True, server_default='000000')
    balance_after_use = db.Column(db.Float, nullable=False, server_default='0')  # balance of the user
    used_at = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        """Returns representative string that displays code and amount of the card"""
        return 'Card #{0}: used by {1} at {2}. Code: {3}'.format(self.uuid, self.user_id, self.used_at, self.code)
