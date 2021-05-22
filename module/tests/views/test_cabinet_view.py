"""Testing route /cabinet"""
from flask_login import current_user
from module.tests import captured_templates, init_app, login_user, logout_user


def test_cabinet_view_access_and_render(init_app):
    """Make sure route '/cabinet' works and template with cabinet form is rendered"""
    app = init_app

    with captured_templates(app) as templates:
        with app.test_client() as client:
            # User is not authenticated
            response_cabinet_view = client.get("/cabinet")
            assert response_cabinet_view.status_code == 302
            assert current_user.is_anonymous

            # Authenticate user
            response_login_user = login_user(client, "john", "test")
            assert response_login_user.status_code == 200
            assert current_user.is_authenticated

            # Template 'cabinet' was rendered
            template, context = templates[-1]
            assert len(templates) == 1
            assert template.name == "cabinet/cabinet.html"

            # Logout user
            response_logout_user = logout_user(client)
            assert response_logout_user.status_code == 200
            assert current_user.is_anonymous

            # Authenticate admin and try to access /cabinet
            response_login_admin = login_user(client, "admin", "test")
            assert response_login_admin.status_code == 200
            assert current_user.is_authenticated and current_user.username == "admin"

            response_cabinet_view_access_for_admin = client.get("/cabinet")
            assert response_cabinet_view_access_for_admin.status_code == 302


def test_payment_card_form(init_app):
    """Check if user can use the payment card"""
    app = init_app

    with app.test_client() as client:
        # login user to access cabinet
        response_login_user = login_user(client, "john", "test")
        assert response_login_user.status_code == 200
        assert current_user.is_authenticated
        assert current_user.balance == 0

        # Use card with code 000001
        response_use_card = client.post("/cabinet", data=dict(code="000001"), follow_redirects=True)
        prev_user_balance = current_user.balance
        assert response_use_card.status_code == 200
        assert current_user.balance != 0

        # Use card with code 000001 again (balance shouldn't change)
        response_use_card = client.post("/cabinet", data=dict(code="000001"), follow_redirects=True)
        assert response_use_card.status_code == 200
        assert current_user.balance == prev_user_balance
