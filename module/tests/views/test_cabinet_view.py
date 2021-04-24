"""Testing route /cabinet"""
from flask_login import current_user
from module.tests import captured_templates, init_app


def test_cabinet_view_access_and_render(init_app):
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
