"""Tests the creation of a copy of the app"""
from flask import Flask
from app import create_app


def test_create_copy_app():
    """Сreating an application with and without params"""

    app = create_app()
    app_with_custom_config = create_app({"SECRET_KEY": "test"})
    assert isinstance(app, Flask) and app_with_custom_config is not None
