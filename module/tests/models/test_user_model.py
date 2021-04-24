"""Test the User model"""
from module.tests import setup_database, dataset
from module.server.models.user import User, load_user


def test_create_and_add_user(dataset):
    """Creating an user object with parameters"""

    db = dataset

    # Creates user object
    usr = User(
        name="Some Name Surname",
        phone="+380961122333",
        email="test@emample.com",
        username="michael",
        tariff="50m",
        ip="197.0.0.1"
    )
    assert usr is not None

    # Add to database
    assert len(db.session.query(User).all()) == 2
    db.session.add(usr)
    db.session.commit()
    assert len(db.session.query(User).all()) == 3
    assert db.session.query(User).get(3).username == 'michael'


def test_password_hash():
    """Compare the string with user password hash"""

    usr = User(
        name="Some Name Surname",
        email="test@emample.com",
        username="john",
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
    )

    assert usr.__repr__() == "User: john"


def test_load_user(dataset):
    """Load user by id"""

    test_user = load_user('1')
    assert test_user.__repr__() == 'User: john'
