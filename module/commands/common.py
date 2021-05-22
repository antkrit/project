"""Common commands for the manager"""
import click
from flask.cli import AppGroup
from sqlalchemy.exc import IntegrityError
from module import App
from module.server.models.user import User
from module.server.models.payment_cards import Card

populate_cli = AppGroup("populate")


@populate_cli.command("admin")
@click.option("-p", "--password", default="test", help="Administrator password.")
def admin(password):
    """
    Creates an admin account if one doesn't exist

    :param password: password for the admin account. In the command line interface,
        you can specify this by giving the -p or --password argument, defaults to 'test'
    :type password: str, optional
    """
    usr = User.query.first()
    if not usr:
        # If the first row in the table doesn't exist
        # Creates account with login "admin" and password "test"(both fields may be changed)
        try:
            admin = User(username="admin", password=password)
            admin.save_to_db()
            # If everything is okay a message with the login and password from the admin account
            # will be displayed in the console
            print("Successfully created.\nLogin: {0}\nPassword: {1}".format("admin", password))
        except Exception as e:
            # If there is troubles with saving to database
            print("Unable to create: {0}".format(e))
    else:
        # If admin already exists - do nothing
        print("Already exists.")


@populate_cli.command("cards")
@click.option("-n", "--num", default=10, help="Number of test cards.")
def cards(num):
    """
    Creates and saves to database test payment cards

    :param num: number of test payment cards with codes 00000i, where i in range(0, num_test_cards)
        and amounts 200, 400 (50 on 50). In the command line interface, you can specify this by giving
        the -n or --num argument, defaults to 10
    :type num: int, optional
    """

    num_200_test_cards = num // 2
    num_400_test_cards = num - num_200_test_cards

    card_codes_list = list()

    # Creates cards with amount 200
    for i in range(num_200_test_cards):
        code = str(i).rjust(6, "0")
        card_codes_list.append(code)

        card = Card(amount=200, code=code)
        App.db.session.add(card)

    # Creates cards with amount 400
    for i in range(num_200_test_cards, num_200_test_cards + num_400_test_cards):
        code = str(i).rjust(6, "0")
        card_codes_list.append(code)

        card = Card(amount=400, code=code)
        App.db.session.add(card)

    try:
        # If everything is okay - payment cards will be added to the database
        App.db.session.commit()
        print("Successfully created. Card codes: {0}".format(card_codes_list))
    except IntegrityError:
        # If there is troubles with saving to database
        print("Cards already exists.")
