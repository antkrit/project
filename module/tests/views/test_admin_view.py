"""Testing route /admin"""
from flask import session
from flask_login import current_user
from module.server.models.user import User, State, Tariffs
from module.tests import captured_templates, init_app, login_user, logout_user


def test_admin_view_access_and_render(init_app):
    """Make sure route '/cabinet' works and template with cabinet form is rendered"""
    app = init_app

    with captured_templates(app) as templates:
        with app.test_client() as client:
            # User is not authenticated
            response_admin_view = client.get('/admin/')
            assert response_admin_view.status_code == 302
            assert current_user.is_anonymous

            # Authenticate user
            response_login_user = login_user(client, 'admin', 'test')
            assert response_login_user.status_code == 200
            assert current_user.is_authenticated

            # Template 'admin' was rendered
            template, context = templates[-1]
            assert len(templates) == 1
            assert template.name == 'admin/admin.html'

            # Logout user
            response_logout_user = logout_user(client)
            assert response_logout_user.status_code == 200
            assert current_user.is_anonymous

            # Authenticate usual user and try to access /admin
            response_login_admin = login_user(client, 'john', 'test')
            assert response_login_admin.status_code == 200
            assert current_user.is_authenticated and current_user.username != 'admin'

            response_admin_view_access_for_admin = client.get('/admin/')
            assert response_admin_view_access_for_admin.status_code == 302


def test_admin_form_buttons(init_app):
    """Make sure all buttons work"""
    app = init_app

    with captured_templates(app) as templates:
        with app.test_client() as client:
            response_login_user = login_user(client, 'admin', 'test')
            assert response_login_user.status_code == 200
            assert current_user.is_authenticated

            # Search
            response_press_search_button = client.post(
                '/admin/',
                data=dict(username='john', search_button=True),
                follow_redirects=True
            )
            assert response_press_search_button.status_code == 200
            assert session['_username_search_form'] == 'john'

            # Register
            response_press_register_button = client.post(
                '/admin/',
                data=dict(username='john', register_button=True),
                follow_redirects=True
            )
            template, context = templates[-1]
            assert response_press_register_button.status_code == 200
            assert template.name == 'auth/register.html'

            # Activate state
            response_press_activate_button = client.post(
                '/admin/',
                data=dict(username='john', activate_button=True),
                follow_redirects=True
            )
            usr = User.query.filter_by(username=session.get('_username_search_form')).first()
            assert response_press_activate_button.status_code == 200
            assert usr.state == State.activated_state.value

            # Deactivate state
            response_press_deactivate_button = client.post(
                '/admin/',
                data=dict(username='john', deactivate_button=True),
                follow_redirects=True
            )
            usr = User.query.filter_by(username=session.get('_username_search_form')).first()
            assert response_press_deactivate_button.status_code == 200
            assert usr.state == State.deactivated_state.value

            # Delete
            response_press_delete_button = client.post(
                '/admin/',
                data=dict(username='john', delete_button=True),
                follow_redirects=True
            )
            assert response_press_delete_button.status_code == 200
            assert not User.query.filter_by(username=session.get('_username_search_form')).first()


def test_register_view(init_app):
    """Tests for the '/admin/register route"""
    app = init_app

    with captured_templates(app) as templates:
        with app.test_client() as client:
            # User is not authenticated
            response_register_view = client.get('/admin/register')
            assert response_register_view.status_code == 302
            assert current_user.is_anonymous

            # Authenticate user
            response_login_user = login_user(client, 'admin', 'test')
            assert response_login_user.status_code == 200
            assert current_user.is_authenticated

            # Get register view
            response_register_view_user_authenticated = client.get('/admin/register')
            assert response_register_view_user_authenticated.status_code == 200

            # Template 'admin' was rendered
            template, context = templates[-1]
            assert template.name == 'auth/register.html'

            # Logout user
            response_logout_user = logout_user(client)
            assert response_logout_user.status_code == 200
            assert current_user.is_anonymous

            # Authenticate usual user and try to access /admin/register
            response_login_admin = login_user(client, 'john', 'test')
            assert response_login_admin.status_code == 200
            assert current_user.is_authenticated and current_user.username != 'admin'

            response_cabinet_view_access_for_admin = client.get('/admin/register')
            assert response_cabinet_view_access_for_admin.status_code == 302


def test_register_new_user(init_app):
    """Make sure registration form is worked"""
    app = init_app

    with captured_templates(app) as templates:
        with app.test_client() as client:
            # Login admin
            response_login_user = login_user(client, 'admin', 'test')
            assert response_login_user.status_code == 200
            assert current_user.is_authenticated and current_user.username == 'admin'

            # Username 'test' doesn't exists
            assert not User.query.filter_by(username='test').first()

            # Register new user
            response_register_view = client.post(
                '/admin/register',
                data=dict(
                    name='Test Surname',
                    phone='+380989898988',
                    email='test@mail.ru',
                    username='test',
                    password='test',
                    tariff=Tariffs.tariff_50m.value['tariff_name'],
                    address='St. Fairy, 23'
                ),
                follow_redirects=True
            )
            template, context = templates[-1]
            assert response_register_view.status_code == 200
            assert User.query.filter_by(username='test').all()
            assert template.name == 'admin/admin.html'

            # Try to register new NON UNIQUE user
            response_register_view = client.post(
                '/admin/register',
                data=dict(
                    name='Test Surname',
                    phone='+380989898988',
                    email='test@mail.ru',
                    username='test',
                    password='test',
                    tariff=Tariffs.tariff_50m.value['tariff_name'],
                    address='St. Fairy, 23'
                ),
                follow_redirects=True
            )
            template, context = templates[-1]
            assert response_register_view.status_code == 200
            assert len(User.query.filter_by(username='test').all()) == 1
            assert template.name == 'auth/register.html'
