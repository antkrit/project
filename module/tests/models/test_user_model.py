"""Test the User model"""
import pytest
from module import App
from module.server.models.user import User, load_user


@pytest.fixture(scope='function')
def setup_database():
    """Fixture to set up the in-memory database"""
    # Init
    runner = App(testing=True)
    app = runner.get_flask_app()
    db = runner.db
    app_context = app.app_context()

    # Setup
    app_context.push()
    db.create_all()
    yield db

    # Teardown
    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture(scope='function')
def dataset(setup_database):

    db = setup_database

    # Creates users
    john = User(username='john')
    andre = User(username='andre')
    db.session.add(john)
    db.session.add(andre)
    db.session.commit()

    yield db


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

