import pytest
from flask import template_rendered
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


def test_login_view_access_and_render(init_app):
    """Make sure route '/cabinet' works and template with cabinet form is rendered"""
    app = init_app

    with captured_templates(app) as templates:
        with app.test_client() as client:
            # User is not authenticated
            response_cabinet_view = client.get('/cabinet')
            assert response_cabinet_view.status_code == 302

            # Authenticate user
            response_login_user = client.post('/',
                                   data=dict(username='john', password='test'),
                                   follow_redirects=True)
            assert current_user.is_authenticated
            assert response_login_user.status_code == 200

        template, context = templates[0]
        assert len(templates) == 1
        assert template.name == 'cabinet/cabinet.html'
