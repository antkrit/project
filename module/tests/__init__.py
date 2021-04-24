import pytest

from flask import template_rendered
from contextlib import contextmanager
from module import App
from module.server.models.user import User
from module.server.view.login import bp as login_bp
from module.server.view.cabinet import bp as cabinet_bp


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
    runner.register_blueprints(login_bp, cabinet_bp)
    app = runner.get_flask_app()
    db = runner.db
    app_context = app.app_context()

    # Setup
    app_context.push()
    db.create_all()

    usr = User(username='john')
    usr.set_password('test')

    db.session.add(usr)
    db.session.commit()
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
    """Populate database"""
    db = setup_database

    # Creates users
    john = User(username='john')
    andre = User(username='andre')
    db.session.add(john)
    db.session.add(andre)
    db.session.commit()

    yield db
