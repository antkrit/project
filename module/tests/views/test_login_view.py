import pytest
from flask import template_rendered
from flask_wtf import FlaskForm
from flask_login import current_user
from contextlib import contextmanager

from module import App
from module.server.models.user import User
from module.server.view.login import bp as login_bp
from module.server.view.cabinet import bp as cabinet_bp


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


def login_user(client, username, password):
    """
    User authorization on POST request to login view

    :param client: test client of the flask application
    :param username: login of the user
    :param password: password of the user
    """
    return client.post('/', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def test_login_view_access_and_render(init_app):
    """Make sure route '/' works and template with login form is rendered"""
    app = init_app

    with captured_templates(app) as templates:

        response = app.test_client().get('/')
        assert response.status_code == 200
        assert len(templates) == 1

        template, context = templates[0]
        assert template.name == 'auth/login.html'
        assert isinstance(context['form'], FlaskForm)


def test_login_view(init_app):
    """Make sure login works"""
    app = init_app

    with app.test_client() as client:
        response_login_bad_login = login_user(client, 'john1', 'test')
        assert response_login_bad_login.status_code == 200
        assert current_user.is_anonymous

        response_login_bad_password = login_user(client, 'john', 'test1')
        assert response_login_bad_password.status_code == 200
        assert current_user.is_anonymous

        response_login = login_user(client, 'john', 'test')
        assert response_login.status_code == 200
        assert current_user.id == 1

        # User is authenticated
        response_login_view = client.get('/')
        assert response_login_view.status_code == 302
