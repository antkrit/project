"""Testing route /"""
from flask_wtf import FlaskForm
from flask_login import current_user
from module.tests import captured_templates, login_user, logout_user, init_app


def test_login_view_access_and_render(init_app):
    """Make sure route '/' works and template with login form is rendered"""
    app = init_app

    with app.test_client() as client:
        with captured_templates(app) as templates:

            # GET request to the route
            response = client.get('/')
            assert response.status_code == 200
            assert len(templates) == 1  # ['auth/login.html']

            # Template 'login' was rendered
            template, context = templates[-1]
            assert template.name == 'auth/login.html'
            assert isinstance(context['form'], FlaskForm)

            # Login admin and try to access login view
            response_login_admin = login_user(client, 'admin', 'test')
            assert response_login_admin.status_code == 200

            response_get_login_view = client.get('/')
            assert len(templates) == 2  # ['auth/login.html', 'admin/admin.html']

            template, context = templates[-1]
            assert response_get_login_view.status_code == 302
            assert template.name == 'admin/admin.html'

            responce_logout_admin = logout_user(client)
            assert len(templates) == 3  # ['auth/login.html', 'admin/admin.html', 'auth/login.html']
            assert responce_logout_admin.status_code == 200
            assert current_user.is_anonymous

            # Login user and try to access login view
            response_login_admin = login_user(client, 'john', 'test')
            assert response_login_admin.status_code == 200

            response_get_login_view = client.get('/')
            assert len(templates) == 4  # [..., 'cabinet/cabinet.html']

            template, context = templates[-1]
            assert response_get_login_view.status_code == 302
            assert template.name == 'cabinet/cabinet.html'


def test_logout(init_app):
    """Tests logout current user"""
    app = init_app

    with app.test_client() as client:
        # Login user 'john'
        response_login = login_user(client, 'john', 'test')
        assert response_login.status_code == 200
        assert current_user.username == 'john'
        assert current_user.is_authenticated

        # Logout user 'john'
        response_logout = logout_user(client)
        assert response_logout.status_code == 200
        assert current_user.is_anonymous


def test_login_view(init_app):
    """Make sure login works"""
    app = init_app

    with app.test_client() as client:
        with captured_templates(app) as templates:
            # Login admin
            responce_login_admin = login_user(client, 'admin', 'test')
            assert responce_login_admin.status_code == 200
            assert current_user.username == 'admin'
            assert current_user.is_authenticated

            # Redirect to admin interface
            template, context = templates[0]
            assert template.name == 'admin/admin.html'

            # Logout admin to continue testing
            responce_logout_admin = logout_user(client)
            assert responce_logout_admin.status_code == 200
            assert current_user.is_anonymous

        # Wrong login
        response_login_bad_login = login_user(client, 'john1', 'test')
        assert response_login_bad_login.status_code == 200
        assert current_user.is_anonymous

        # Wrong password
        response_login_bad_password = login_user(client, 'john', 'test1')
        assert response_login_bad_password.status_code == 200
        assert current_user.is_anonymous

        # Successful login
        response_login = login_user(client, 'john', 'test')
        assert response_login.status_code == 200
        assert current_user.is_authenticated

        # User is authenticated
        response_login_view = client.get('/')
        assert response_login_view.status_code == 302
