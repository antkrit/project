"""Tests for user resource"""
import json
from uuid import uuid4
from flask import url_for
from flask_jwt_extended import decode_token
from module.tests import init_app, get_access_token
from module.server.models.user import User
from module.server.models.jwt_tokens import TokenBlocklist


def test_auth_resource(init_app):
    """Tests AuthResource"""
    app = init_app

    with app.test_client() as client:
        # GET
        response_get_route_no_headers = client.get(url_for('api_auth'))
        assert response_get_route_no_headers.status_code == 400

        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })

        response_get_route = client.get(
            url_for('api_auth'),
            headers={'Content-Type': 'application/json'},
            data=login_payload_john
        )
        assert response_get_route.status_code == 200
        for key_ in ['access_token', 'refresh_token', 'fresh', 'expires_in']:
            assert key_ in response_get_route.json.keys()
        assert response_get_route.json.get('fresh')

        login_payload_not_found = json.dumps({
            "login": "invalid",
            "password": "test"
        })
        response_get_route_404 = client.get(
            url_for('api_auth'),
            headers={'Content-Type': 'application/json'},
            data=login_payload_not_found
        )
        assert response_get_route_404.status_code == 401

        # POST
        register_payload = json.dumps({
            "address": "St.Test",
            "name": "Test Test",
            "email": "test1@test.com",
            "password": "test",
            "phone": "+380967711222",
            "tariff": "50m",
            "username": "test"
        })
        register_payload_non_unique = json.dumps({
            "address": "St.Test",
            "name": "Test Test",
            "email": "test1@test.com",
            "password": "test",
            "phone": "+380967711222",
            "tariff": "50m",
            "username": "test-another"
        })
        login_payload_admin = json.dumps({
            "login": "admin",
            "password": "test"
        })
        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })

        response_login_john = client.get(
            url_for('api_auth'),
            headers={"Content-Type": "application/json"},
            data=login_payload_john
        )
        assert response_login_john.status_code == 200

        response_post_route_auth_not_admin = client.post(
            url_for('api_auth'),
            headers={
                'Authorization': 'Bearer {0}'.format(response_login_john.json.get('access_token')),
                'Content-Type': 'application/json'
            },
            data=register_payload
        )
        assert response_post_route_auth_not_admin.status_code == 403

        response_login_admin = client.get(
            url_for('api_auth'),
            headers={"Content-Type": "application/json"},
            data=login_payload_admin
        )
        assert response_login_admin.status_code == 200
        access_token_admin = response_login_admin.json.get('access_token')

        assert not User.get_user_by_username('test')
        response_post_route_auth = client.post(
            url_for('api_auth'),
            headers={
                'Authorization': 'Bearer {0}'.format(access_token_admin),
                'Content-Type': 'application/json'
            },
            data=register_payload
        )
        assert response_post_route_auth.status_code == 201
        assert User.get_user_by_username('test')

        response_post_route_auth_user_exists = client.post(
            url_for('api_auth'),
            headers={
                'Authorization': 'Bearer {0}'.format(access_token_admin),
                'Content-Type': 'application/json'
            },
            data=register_payload
        )
        assert response_post_route_auth_user_exists.status_code == 400

        response_post_route_auth_user_exists = client.post(
            url_for('api_auth'),
            headers={
                'Authorization': 'Bearer {0}'.format(access_token_admin),
                'Content-Type': 'application/json'
            },
            data=register_payload_non_unique
        )
        assert response_post_route_auth_user_exists.status_code == 500


def test_logout_resource(init_app):
    """Tests LogoutResource"""
    app = init_app

    with app.test_client() as client:
        response_get_route_no_headers = client.post(url_for('api_logout'))
        assert response_get_route_no_headers.status_code == 401

        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })
        access_token = get_access_token(client, login_payload_john)
        decoded = decode_token(access_token)

        response_logout = client.post(
            url_for('api_logout'),
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )
        assert response_logout.status_code == 200
        assert TokenBlocklist.query.filter_by(jti=decoded.get('jti'))


def test_user_resource(init_app):
    """Tests UserResource"""
    app = init_app
    user_john = User.get_user_by_username('john')
    user_andre = User.get_user_by_username('andre')

    with app.test_client() as client:
        # GET
        response_get_route_no_headers_no_auth = client.get(url_for('api_user_details', uuid=user_john.uuid))
        assert response_get_route_no_headers_no_auth.status_code == 401

        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })
        access_token = get_access_token(client, login_payload_john)

        response_get_user_route_john_uuid_andre = client.get(
            url_for('api_user_details', uuid=user_andre.uuid),
            headers={'Authorization': 'Bearer {0}'.format(access_token)},
        )
        assert response_get_user_route_john_uuid_andre.status_code == 403

        response_get_user_route_john_uuid_john = client.get(
            url_for('api_user_details', uuid=user_john.uuid),
            headers={'Authorization': 'Bearer {0}'.format(access_token)},
        )
        assert response_get_user_route_john_uuid_john.status_code == 200
        for key_ in ['name', 'email', 'phone']:
            assert key_ in response_get_user_route_john_uuid_john.json.keys()

        login_payload_admin = json.dumps({
            "login": "admin",
            "password": "test"
        })
        access_token = get_access_token(client, login_payload_admin)

        response_get_user_route_admin_uuid_john = client.get(
            url_for('api_user_details', uuid=user_john.uuid),
            headers={'Authorization': 'Bearer {0}'.format(access_token)},
        )
        assert response_get_user_route_admin_uuid_john.status_code == 200
        for key_ in ['name', 'email', 'phone']:
            assert key_ not in response_get_user_route_admin_uuid_john.json.keys()

        response_get_user_route_admin_uuid_john = client.get(
            url_for('api_user_details', uuid=uuid4()),
            headers={'Authorization': 'Bearer {0}'.format(access_token)},
        )
        assert response_get_user_route_admin_uuid_john.status_code == 404

        # POST
        response_get_route_no_headers_no_auth = client.post(url_for('api_user_details', uuid=user_john.uuid))
        assert response_get_route_no_headers_no_auth.status_code == 401

        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })
        access_token = get_access_token(client, login_payload_john)

        response_post_user_route_john_uuid_andre = client.post(
            url_for('api_user_details', uuid=user_andre.uuid),
            headers={'Authorization': 'Bearer {0}'.format(access_token)},
        )
        assert response_post_user_route_john_uuid_andre.status_code == 403

        response_post_user_route_john_uuid_john_no_content = client.post(
            url_for('api_user_details', uuid=user_john.uuid),
            headers={'Authorization': 'Bearer {0}'.format(access_token)},
        )
        assert response_post_user_route_john_uuid_john_no_content.status_code == 400

        response_post_user_route_john_uuid_john_invalid_card_code = client.post(
            url_for('api_user_details', uuid=user_john.uuid),
            headers={
                'Authorization': 'Bearer {0}'.format(access_token),
                'Content-Type': 'application/json'
            },
            data=json.dumps({'code': 'invalid'})
        )
        assert response_post_user_route_john_uuid_john_invalid_card_code.status_code == 404

        assert User.get_user_by_username('john').balance == 0
        response_post_user_route_john_uuid_john_valid_card_code = client.post(
            url_for('api_user_details', uuid=user_john.uuid),
            headers={
                'Authorization': 'Bearer {0}'.format(access_token),
                'Content-Type': 'application/json'
            },
            data=json.dumps({'code': '000001'})
        )
        assert response_post_user_route_john_uuid_john_valid_card_code.status_code == 200
        assert User.get_user_by_username('john').balance != 0


def test_user_history_resource(init_app):
    """Tests UserHistoryResource"""
    app = init_app
    user_john = User.get_user_by_username('john')

    with app.test_client() as client:
        response_get_route_no_auth = client.get(url_for('api_user_history', uuid=user_john.uuid))
        assert response_get_route_no_auth.status_code == 401

        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })
        access_token = get_access_token(client, login_payload_john)

        response_get_user_history_wrong_uuid = client.get(
            url_for('api_user_history', uuid=uuid4()),
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )
        assert response_get_user_history_wrong_uuid.status_code == 404

        response_get_user_history_wrong_uuid = client.get(
            url_for('api_user_history', uuid=user_john.uuid),
            headers={'Authorization': 'Bearer {0}'.format(access_token)}
        )
        assert response_get_user_history_wrong_uuid.status_code == 200


def test_users_resource(init_app):
    """Tests UsersResource"""
    app = init_app
    user_john = User.get_user_by_username('john')

    with app.test_client() as client:
        response_get_route_no_auth = client.get(url_for('api_user_history', uuid=user_john.uuid))
        assert response_get_route_no_auth.status_code == 401

        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })
        access_token_john = get_access_token(client, login_payload_john)

        response_get_users_not_admin = client.get(
            url_for('api_users'),
            headers={'Authorization': 'Bearer {0}'.format(access_token_john)}
        )
        assert response_get_users_not_admin.status_code == 200
        assert isinstance(response_get_users_not_admin.json, dict)
        assert response_get_users_not_admin.json.get('username') == 'john'

        login_payload_admin = json.dumps({
            "login": "admin",
            "password": "test"
        })
        access_token_admin = get_access_token(client, login_payload_admin)

        response_get_users_admin = client.get(
            url_for('api_users'),
            headers={'Authorization': 'Bearer {0}'.format(access_token_admin)}
        )
        assert response_get_users_admin.status_code == 200
        assert isinstance(response_get_users_admin.json, list)


def test_refresh_token(init_app):
    """Tests TokenRefresh resource"""
    app = init_app

    with app.test_client() as client:
        response_get_route_no_auth = client.post(url_for('api_refresh'))
        assert response_get_route_no_auth.status_code == 401

        login_payload_john = json.dumps({
            "login": "john",
            "password": "test"
        })
        response_get_login_route_admin = client.get(
            url_for('api_auth'),
            headers={'Content-Type': 'application/json'},
            data=login_payload_john
        )
        refresh_token = response_get_login_route_admin.json.get('refresh_token')

        response_get_refresh = client.post(
            url_for('api_refresh'),
            headers={'Authorization': 'Bearer {0}'.format(refresh_token)}
        )
        assert response_get_refresh.status_code == 200
        for key_ in ['access_token', 'refresh_token', 'fresh', 'expires_in']:
            assert key_ in response_get_refresh.json.keys()
        assert not response_get_refresh.json.get('fresh')
