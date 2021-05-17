"""Test the User model"""
from module.tests import setup_database, dataset
from module.server.models.user import User, State, load_user


def test_create_and_add_user(dataset):
    """Creating an user object with parameters"""

    db = dataset

    # User object
    usr = User(
        name="Some Name Surname",
        phone="+380961122333",
        email="test@emample.com",
        username="michael",
        password='test',
        tariff="50m",
    )
    assert usr is not None

    # Add to database
    assert len(db.session.query(User).all()) == 2
    db.session.add(usr)
    db.session.commit()
    assert len(db.session.query(User).all()) == 3
    assert db.session.query(User).get(3).username == 'michael'


def test_password_hash(setup_database):
    """Compare the string with user password hash"""

    usr = User(
        name="Some Name Surname",
        email="test@emample.com",
        username="john",
        password='test'
    )

    assert not usr.check_password("cat")


def test_repr_user(setup_database):
    """Checks whether the user is correctly represented"""

    usr = User(
        name="Some Name Surname",
        phone="+380961122333",
        email="test@emample.com",
        username="john",
        password='test'
    )

    assert usr.__repr__() == "User: john"


def test_change_state_and_set_ip(setup_database):
    """Test state change method"""
    usr = User(
        username="john",
        password='test',
        state=State.activated_state.value
    )

    # Activate
    usr.change_state(deactivate=False)
    assert usr.state == State.activated_state.value

    # Deactivate
    usr.change_state(deactivate=True)
    assert usr.state == State.deactivated_state.value

    # Set new ip
    prev_ip = usr.ip
    assert not usr.ip or prev_ip
    usr.set_ip()
    assert usr.ip and usr.ip != prev_ip and len(usr.ip.split('.')) == 4

    # Set new UNIQUE ip
    test_ip = usr.ip
    usr.set_ip(test_ip=test_ip)
    assert usr.ip != test_ip


def test_saving_deleting_to_db(setup_database):
    """Save and delete user from the database"""
    db = setup_database

    usr = User(username="susan", password='test')
    assert not db.session.query(User).filter_by(username='susan').first()

    usr.save_to_db()
    assert User.get_user_by_username('susan')

    usr.save_to_db()
    assert len(db.session.query(User).filter_by(username='susan').all()) == 1

    usr.delete_from_db()
    assert not User.get_user_by_username('susan')

    prev_num_objects = len(db.session.query(User).all())
    try:
        usr_not_exist = User(username="non-exist", password='test')
        usr_not_exist.delete_from_db()
        assert False  # If user was deleted - something goes wrong
    except ValueError:  # Exception was raised - everything is OK
        assert len(db.session.query(User).all()) == prev_num_objects


def test_load_user(dataset):
    """Load user by id"""
    test_user = load_user('1')
    assert test_user.__repr__() == 'User: john'
