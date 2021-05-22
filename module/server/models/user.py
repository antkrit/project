"""User database model"""
from enum import Enum
from random import randint
from datetime import datetime, timezone
from flask import flash
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from module import App
from module.server import messages
from module.server.models import generate_uuid, Base
from module.server.models.payment_cards import Card, UsedCard


db = App.db
login_manager = App.login_manager


class Tariffs(Enum):
    """Available tariffs"""

    tariff_50m = dict(tariff_name="50m", cost=100)
    tariff_100m = dict(tariff_name="100m", cost=200)
    tariff_200m = dict(tariff_name="200m", cost=300)
    tariff_500m = dict(tariff_name="500m", cost=500)


class State(Enum):
    """Available states for the account"""

    activated_state = "activated"
    deactivated_state = "deactivated"


class User(Base, UserMixin, db.Model):
    """
    User table

    :param username: login of the user
    :type username: str
    :param password: password of the user
    :type password: str
    :param name: full name of the user, defaults to None
    :type name: str, optional
    :param email: email of the user, defaults to None
    :type email: str, optional
    :param phone: phone of the user, defaults to None
    :type phone: str, optional
    :param address: home address of the user, defaults to None
    :type address: str, optional
    :param tariff: tariff plan of the user, defaults to None
    :type tariff: class:'Tariffs', optional
    :param state: user account state, defaults to None
    :type state: class:'State', optional
    :param uuid: custom uuid of the user, defaults to None
    :type uuid: str, optional
    """

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, index=True, unique=True, default=generate_uuid)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tariff = db.Column(db.String(32))
    ip = db.Column(db.String(64))
    address = db.Column(db.String(64))
    state = db.Column(db.String(64), server_default=State.deactivated_state.value)
    balance = db.Column(db.Float, default=0)

    used_cards = db.relationship("UsedCard", backref="user", lazy="dynamic")

    def __init__(
        self,
        username,
        password,
        name=None,
        email=None,
        phone=None,
        address=None,
        tariff=None,
        state=None,
        uuid=None,
    ):
        self.uuid = uuid
        self.username = username
        self.set_password(password)
        self.name = name
        self.email = email
        self.phone = phone
        self.tariff = tariff
        self.address = address
        self.state = state
        self.set_ip()

    def get_info(self) -> list:
        """Returns list of user information"""
        return [
            self.address,
            self.name,
            self.ip,
            self.phone,
            self.email,
            self.tariff,
            self.balance,
            self.state,
        ]

    def change_state(self, deactivate=False) -> None:
        """
        Change state of the account.
        :param deactivate: determines whether to deactivate the account (if True) or activate (if False),
            defaults to False
        :type deactivate: bool, optional
        """
        self.state = State.activated_state.value if not deactivate else State.deactivated_state.value
        db.session.commit()

    def use_card(self, card_code) -> None:
        """
        Add money to the user's balance and makes the card inactive if the card code exists in the database.
        :param card_code: card code to activate it.
        :type card_code: str
        """
        card = Card.get_card_by_code(code=card_code)
        if card:  # if code is correct
            self.balance += card.amount
            used = UsedCard(
                amount=card.amount,
                code=card_code,
                balance_after_use=self.balance,
                used_at=datetime.now(timezone.utc),
                user_id=self.id,
            )

            used.save_to_db()
            card.delete_from_db()
            flash(messages["card_success_code"], "info")
        else:
            flash(messages["card_wrong_code"], "warning")

    def get_history(self) -> list:
        """Returns payments history (last 10 rows)"""
        return self.used_cards.order_by(UsedCard.id.desc()).limit(10)

    def set_password(self, password) -> None:
        """
        Sets password hash by string "password".
        The original password isn't stored anywhere.
        :param password: the password by which the user will be logged in in the future
        :type password: str
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        """
        Compare password hash with string "password".
        Returns true if they match. Otherwise - false.
        :param password: the password you need to compare with the current user password
        :type password: str
        """
        return check_password_hash(self.password_hash, password)

    def set_ip(self, test_ip=None) -> None:
        """
        Generates and sets a random ip.
        :param test_ip: ip address that can be entered manually, defaults to None
        :type test_ip:str, optional
        """
        rand_ip = ".".join([str(randint(0, 255)) for _ in range(4)]) if not test_ip else test_ip
        # if such ip doesn't yet exist and there is no test ip
        if not db.session.query(User).filter_by(ip=rand_ip).first() and not test_ip:
            self.ip = rand_ip
            db.session.commit()
            return

        self.set_ip()  # otherwise run this function again

    @classmethod
    def get_user_by_username(cls, username) -> "User":
        """
        Get user from database by it's username
        :param username: username of the user
        :type username: str
        """
        return db.session.query(cls).filter_by(username=username).first()

    def __repr__(self) -> str:
        """Returns representative string that displays the username of the user"""
        return "User: {}".format(self.username)


@login_manager.user_loader
def load_user(id_) -> "User":
    """Flask-Login user loader function"""
    return User.query.get(int(id_))
