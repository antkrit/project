"""Tests the creation of a copy of the app"""
import os
import logging
from flask import Flask
from module import App
from module.server.view.login import bp as login_bp
from module.server.view.admin import bp as admin_bp


def test_create_testing_app():
    """Сreating an application with test mode"""

    # Test mode
    app = App(testing=True).get_flask_app()
    assert isinstance(app, Flask) and app.testing

    app = App().get_flask_app()
    assert isinstance(app, Flask) and not app.testing

    runner = App()
    app = runner.get_flask_app()
    assert os.path.exists(runner.templates_folder)
    assert os.path.exists(runner.static_folder)
    assert os.path.exists(runner.migration_folder)
    assert os.path.exists(runner.logs_folder)

    assert app.logger.level == logging.DEBUG
    runner.setup_logging_error_handling(log_level=logging.ERROR)
    assert app.logger.level == logging.ERROR

    prev_len = len(list(app.url_map.iter_rules()))
    runner.register_blueprints(login_bp, admin_bp)
    assert len(list(app.url_map.iter_rules())) != prev_len
