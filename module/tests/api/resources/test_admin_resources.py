"""Tests for admin resource"""
import json
from flask import url_for
from module.tests import init_app, get_access_token
from module.server.models.user import User, State


def test_admin_tools_resource(init_app):
    """Tests AdminToolsResource"""
    app = init_app
    user = User.get_user_by_username("john")
    user_to_del = User.get_user_by_username("test_del")

    with app.test_client() as client:
        response_get_route_no_auth = client.post(url_for("api_admin_tools", uuid=user.uuid))
        assert response_get_route_no_auth.status_code == 401

        login_payload_john = json.dumps({"login": "john", "password": "test"})
        login_payload_admin = json.dumps({"login": "admin", "password": "test"})

        access_token_john = get_access_token(client, login_payload_john)
        response_get_route_not_admin_auth = client.post(
            url_for("api_admin_tools", uuid=user.uuid),
            headers={"Authorization": "Bearer {0}".format(access_token_john)},
        )
        assert response_get_route_not_admin_auth.status_code == 403
        access_token_admin = get_access_token(client, login_payload_admin)

        response_get_route_admin_auth_no_content_type = client.post(
            url_for("api_admin_tools", uuid=user.uuid),
            headers={"Authorization": "Bearer {0}".format(access_token_admin)},
        )
        assert response_get_route_admin_auth_no_content_type.status_code == 400

        response_get_route_admin_deactivate = client.post(
            url_for("api_admin_tools", uuid=user.uuid),
            headers={
                "Authorization": "Bearer {0}".format(access_token_admin),
                "Content-Type": "application/json",
            },
            data=json.dumps({"choice": "deactivate"}),
        )
        assert response_get_route_admin_deactivate.status_code == 200
        assert user.state == State.deactivated_state.value

        response_get_route_admin_activate = client.post(
            url_for("api_admin_tools", uuid=user.uuid),
            headers={
                "Authorization": "Bearer {0}".format(access_token_admin),
                "Content-Type": "application/json",
            },
            data=json.dumps({"choice": "activate"}),
        )
        assert response_get_route_admin_activate.status_code == 200
        assert user.state == State.activated_state.value

        response_get_route_admin_delete = client.post(
            url_for("api_admin_tools", uuid=user_to_del.uuid),
            headers={
                "Authorization": "Bearer {0}".format(access_token_admin),
                "Content-Type": "application/json",
            },
            data=json.dumps({"choice": "delete"}),
        )
        assert response_get_route_admin_delete.status_code == 200
        assert not User.get_user_by_username("test_del")

        response_get_route_admin_delete_no_user = client.post(
            url_for("api_admin_tools", uuid=user_to_del.uuid),
            headers={
                "Authorization": "Bearer {0}".format(access_token_admin),
                "Content-Type": "application/json",
            },
            data=json.dumps({"choice": "delete"}),
        )
        assert response_get_route_admin_delete_no_user.status_code == 500
