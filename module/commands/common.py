"""Common commands for the manager"""
import pytest
from flask_script import Command, Manager
from module import App
from module.server.models.user import User, Tariffs, State
from module.server.models.payment_cards import Card, UsedCard


class PytestCommand(Command):
    """Runs tests"""
    capture_all_args = True

    def __call__(self, app=None, *args):
        pytest.main(*args)


def make_context_():
    """Returns dictionary for the shell context"""
    return dict(App=App, db=App.db, User=User, Tariffs=Tariffs, State=State, Card=Card, UsedCard=UsedCard)


populate_manager = Manager(usage="Populate database with test data")


@populate_manager.command
def admin(password='test'):
    """Creates an admin account if one doesn't exist"""
    usr = User.query.first()
    if not usr:
        # If the first row in the table doesn't exist
        # Creates account with login "admin" and password "test"(both fields may be changed)
        try:
            admin = User(
                username='admin',
                password=password
            )
            admin.save_to_db()
            print("Successfully created.\nLogin: {0}\nPassword: {1}".format('admin', password))
        except Exception as e:
            print("Unable to create: {0}".format(e))
    else:
        print("Already exists.")


@populate_manager.command
def cards(num_test_cards=10):
    """Creates test payment cards"""

    num_200_test_cards = num_test_cards // 2
    num_400_test_cards = num_test_cards - num_200_test_cards

    # Creates cards with amount 200
    for i in range(num_200_test_cards):
        card = Card(
            amount=200,
            code=str(i).rjust(6, '0')
        )
        App.db.session.add(card)

    # Creates cards with amount 400
    for i in range(num_200_test_cards, num_200_test_cards + num_400_test_cards):
        card = Card(
            amount=400,
            code=str(i).rjust(6, '0')
        )
        App.db.session.add(card)

    try:
        App.db.session.commit()
        print("Successfully created.")
    except Exception as e:
        print("Unable to create: {0}".format(e))
