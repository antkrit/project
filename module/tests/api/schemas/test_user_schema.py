"""Tests for user-related schemas"""
from module.tests import init_app
from module.server.models.user import User
from module.server.api.schemas.user import RegisterSchema


def test_register_schema_post_load(init_app):
    """Tests create_new_user method"""
    user = RegisterSchema().create_new_user(data={"username": "john", "password": "1234"})
    assert isinstance(user, User) and user.username == "john"
