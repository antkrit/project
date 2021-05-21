"""Tests the creation of a copy of the app"""
import os
import logging
from flask import Flask
from module import App
from module.commands.common import populate_cli
from module.server.models.user import User
from module.server.models.payment_cards import Card
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

    assert populate_cli not in app.cli.commands
    runner.register_cli_commands(populate_cli)
    assert populate_cli in app.cli.commands.values()


def test_cli_commands():
    """Test custom cli commands"""
    app_runner = App(testing=True)
    app = app_runner.get_flask_app()
    db = app_runner.db
    with app.app_context():
        db.create_all()
        cli_runner = app.test_cli_runner()

        # Test 'populate'

        result = cli_runner.invoke(populate_cli, ['admin', '-p', 'test1'])
        assert 'Successfully created.\nLogin: {0}\nPassword: {1}'.format('admin', 'test1') in result.output
        adm_user = db.session.query(User).filter_by(username='admin').first()
        assert adm_user and adm_user.check_password('test1')

        result = cli_runner.invoke(populate_cli, ['admin'])
        assert 'Already exists.' in result.output

        result = cli_runner.invoke(populate_cli, ['cards', '-n', '15'])
        assert 'Successfully created. Card codes:' in result.output
        assert len(db.session.query(Card).all()) == 15

        result = cli_runner.invoke(populate_cli, ['cards'])
        assert 'Cards already exists.' in result.output
