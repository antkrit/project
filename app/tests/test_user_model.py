"""Test the User model"""
from ..models.user import User


def test_create_and_add_user():
    """Checks the possibility of creating an object"""
    usr = User(
        name="Some Name Surname",
        phone="+380961122333",
        email="test@emample.com",
        username="john",
        tariff="50m",
        ip="197.0.0.1"
    )

    assert usr is not None


def test_password_hash():
    """Checks the possibility to compare the string with password hash"""
    usr = User(
        name="Some Name Surname",
        phone="+380961122333",
        email="test@emample.com",
        username="john",
        tariff="50m",
        ip="197.0.0.1"
    )
    usr.set_password("dog")

    assert not usr.check_password("cat")


def test_repr_user():
    """Checks whether the user is correctly represented"""
    usr = User(
        name="Some Name Surname",
        phone="+380961122333",
        email="test@emample.com",
        username="john",
        tariff="50m",
        ip="197.0.0.1"
    )

    assert usr.__repr__() == "User: john"
