"""User database model"""
from enum import Enum
from uuid import uuid4
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from module import App
from module.server.models.payment_cards import Card, UsedCard


db = App.db
login_manager = App.login_manager


class Tariffs(Enum):
    """Available tariffs"""
    tariff_50m = dict(tariff_name='50m', cost=100)
    tariff_100m = dict(tariff_name='100m', cost=200)
    tariff_200m = dict(tariff_name='200m', cost=300)
    tariff_500m = dict(tariff_name='500m', cost=500)


class State(Enum):
    """Available states for the account"""
    activated_state = 'activated'
    deactivated_state = 'deactivated'


class User(UserMixin, db.Model):
    """User table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tariff = db.Column(db.String(32))
    ip = db.Column(db.String(64))
    address = db.Column(db.String(64))
    state = db.Column(db.String(64), server_default=State.deactivated_state.value)
    balance = db.Column(db.Float, server_default='0')

    used_cards = db.relationship('UsedCard', backref='user', lazy='dynamic')

    def get_info(self) -> list:
        """Returns information required for the table in the cabinet"""
        return [self.address, self.name, self.ip, self.phone, self.email, self.tariff, self.balance, self.state]

    def use_card(self, card_code: str):
        """
        Add money to the user's balance and makes the card inactive if the card code exists in the database.

        :param card_code: card code to activate it.
        """
        card = Card.get_card_by_code(code=card_code)
        if card:  # if code is correct
            self.balance += card.amount
            used = UsedCard(
                uuid=str(uuid4()),
                amount=card.amount,
                code=card_code,
                balance_after_use=self.balance,
                used_at=datetime.now(timezone.utc),
                user_id=self.id
            )

            db.session.add(used)
            db.session.delete(card)
            db.session.commit()

    def get_history(self):
        """Returns payments history"""
        return self.used_cards.all()

    def set_password(self, password: str):
        """
        Sets password hash by string "password".
        The original password isn't stored anywhere.

        :param password: the password by which the user will be logged in in the future
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Compare password hash with string "password".
        Returns true if they match. Otherwise - false.

        :param password: the password you need to compare with the current user password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """Returns representative string that displays the username of the user"""
        return 'User: {}'.format(self.username)


@login_manager.user_loader
def load_user(id_: str) -> User:
    """Flask-Login user loader function"""
    return User.query.get(int(id_))
