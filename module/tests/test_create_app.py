"""Tests the creation of a copy of the app"""
from flask import Flask
from module import App


def test_create_testing_app():
    """Сreating an application with test mode"""

    app = App(testing=True).get_flask_app()
    assert isinstance(app, Flask) and app.testing
