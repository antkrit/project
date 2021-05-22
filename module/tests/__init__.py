"""Setup fixtures and common functions"""
import json
import pytest
from flask import template_rendered, url_for
from contextlib import contextmanager
from module import App
from module.server.models.user import User
from module.server.models.payment_cards import Card
from module.server.view.login import bp as login_bp
from module.server.view.cabinet import bp as cabinet_bp
from module.server.view.admin import bp as admin_bp


@contextmanager
def captured_templates(app):
    """Determines which templates were rendered and what variables were passed to the template"""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)

    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def init_app():
    """Init and return app in test mode with in-memory database"""

    # Init
    runner = App(testing=True)
    runner.register_blueprints(login_bp, cabinet_bp, admin_bp)
    app = runner.get_flask_app()
    db = runner.db
    app_context = app.app_context()

    # Setup
    app_context.push()
    db.create_all()

    adm_usr = User(username="admin", password="test")
    db.session.add(adm_usr)

    to_test_del = User(username="test_del", password="test")
    db.session.add(to_test_del)

    usr = User(username="john", password="test")
    db.session.add(usr)

    usr1 = User(username="andre", password="test")
    db.session.add(usr1)

    for i in range(2):
        card = Card(amount=200, code=str(i).rjust(6, "0"))
        db.session.add(card)

    for i in range(2, 4):
        card = Card(amount=400, code=str(i).rjust(6, "0"))
        db.session.add(card)

    db.session.commit()
    with app.test_request_context():
        yield app

    # Teardown
    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture
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


@pytest.fixture
def dataset(setup_database):
    """
    Populate in-memory database.
    :param setup_database: pytest fixture
    """
    db = setup_database

    # Creates users
    john = User(username="john", password="test")
    andre = User(username="andre", password="test")
    db.session.add(john)
    db.session.add(andre)
    db.session.commit()

    yield db


def login_user(client, username, password):
    """
    User authorization on POST request to login view
    :param client: test client of the flask application
    :param username: login of the user
    :param password: password of the user
    """
    return client.post("/", data=dict(username=username, password=password), follow_redirects=True)


def logout_user(client):
    """
    User logout on POST request to logout iew
    :param client: test client of the flask application
    """
    return client.get("/logout", follow_redirects=True)


def get_access_token(client, data):
    """
    Returns access_token if login and password from the request match
    :param client: test client of the flask application
    :param data: data to be sent in the request(login, password)
    """
    response_get_login_route_admin = client.get(
        url_for("api_auth"), headers={"Content-Type": "application/json"}, data=data
    )
    return response_get_login_route_admin.json.get("access_token")
