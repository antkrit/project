"""Model for user account"""
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tariff = db.Column(db.String(32))
    ip = db.Column(db.String(64))
    address = db.Column(db.String(64))

    def __repr__(self) -> str:
        """Returns representative string that displays the username"""
        return 'User: {}'.format(self.username)

    def set_password(self, password: str):
        """
        Sets password hash by string "password"

        :param password: the password by which the user will be logged in in the future
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Compare password hash with string "password"

        :param password: the password you need to compare with the current user password
        """
        return check_password_hash(self.password_hash, password)
