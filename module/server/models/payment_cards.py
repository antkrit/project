"""Payment cards database models"""
from datetime import datetime
from module import App
from module.server.models import Base, generate_uuid


db = App.db


class Card(Base, db.Model):
    """Payment cards table"""

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True, unique=True, default=generate_uuid)
    amount = db.Column(db.Integer, nullable=False, default=0)
    code = db.Column(db.String(64), nullable=False, index=True, unique=True, server_default="000000")

    @classmethod
    def get_card_by_code(cls, code) -> "Card":
        """
        Returns card by it's code if any, otherwise None
        :param code: code of the card
        :type code: str
        """
        return cls.query.filter_by(code=code).first()

    def __repr__(self) -> str:
        """Returns representative string that displays code and amount of the card"""
        return "Card {0}: {1}. Code: {2}".format(self.uuid, self.amount, self.code)


class UsedCard(Base, db.Model):
    """Used payment cards table"""

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True, unique=True, default=generate_uuid)
    amount = db.Column(db.Integer, nullable=False, default=0)
    code = db.Column(db.String(64), nullable=False, index=True, unique=True, server_default="000000")
    balance_after_use = db.Column(db.Float, nullable=False, default=0)  # balance of the user
    used_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @classmethod
    def get_card_by_code(cls, code) -> "UsedCard":
        """
        Returns card by it's code if any, otherwise None
        :param code: code of the card
        :type code: str
        """
        return cls.query.filter_by(code=code).first()

    def __repr__(self) -> str:
        """Returns representative string that displays code, amount of the card, when and by whom it was used"""
        return "Card {0}: used by {1} at {2}. Code: {3}".format(self.uuid, self.user_id, self.used_at, self.code)
