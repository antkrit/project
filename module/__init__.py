"""Initializes all dependencies and creates apps"""
import os
import logging
from json import load
from datetime import timedelta
from logging.handlers import RotatingFileHandler, SMTPHandler
from marshmallow import ValidationError
from flask import Flask, session, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from module.server.config import Config, TestConfig


__version__ = "1.0.4"


class App:
    """
    Creates and configures the flask app (Application-factory)

    :param testing: determines whether to create a program in test mode, defaults to False
    :type testing: bool, optional
    :param config_obj: custom config object, defaults to class:'config.Config'
    :type config_obj: object, optional
    """

    db = SQLAlchemy()
    migrate = Migrate()
    ma = Marshmallow()
    moment = Moment()
    jwt = JWTManager()
    login_manager = LoginManager()
    login_manager.login_view = "login.login_view"
    login_manager.session_protection = "strong"

    def __init__(self, testing=False, config_obj=Config):
        # Folders
        self.migration_folder = os.path.join(os.path.dirname(__file__), "server", "models", "migrations")
        self.templates_folder = os.path.join(os.path.dirname(__file__), "client", "templates")
        self.static_folder = os.path.join(os.path.dirname(__file__), "client", "static")
        self.logs_folder = os.path.join(os.path.dirname(__file__), "server", "static", "logs")

        # App
        self._app = Flask(
            __name__,
            template_folder=self.templates_folder,
            static_folder=self.static_folder,
        )
        if testing:  # Choose configuration
            self._app.config.from_object(TestConfig)
        else:
            self._app.config.from_object(config_obj)

        # Init
        App.db.init_app(self._app)
        with self._app.app_context():  # Fixing ALTER table SQLite issue
            if App.db.engine.url.drivername == "sqlite":
                App.migrate.init_app(
                    self._app,
                    App.db,
                    render_as_batch=True,
                    directory=self.migration_folder,
                )
            else:
                App.migrate.init_app(self._app, App.db, directory=self.migration_folder)

        App.ma.init_app(self._app)
        App.login_manager.init_app(self._app)
        App.moment.init_app(self._app)
        App.jwt.init_app(self._app)

        # Api
        from module.server.api.resources import api

        api.init_app(self._app)

        self.setup_logging_error_handling()

        @self._app.before_request
        def before_request() -> None:
            """
            Updates the session time before each request to server. Sets it to 5 minutes (may be changed).
            To change the possible period of user inactivity - change the argument of the timedelta function.
            If this period is over, user will be automatically redirected to the login page.
            """
            session.permanent = True
            self._app.permanent_session_lifetime = timedelta(minutes=5)

    def register_blueprints(self, *args) -> None:
        """
        Registers blueprints required for the application routes to work.
        To register a new blueprint, just pass it to arguments along with the others.

        :param '*args': the variable arguments are used to get a list of blueprints.
        """
        for bp in args:
            try:
                self._app.register_blueprint(bp)
            except Exception as e:
                self._app.logger.error("An error occurred while registration blueprint - {}".format(e))

    def register_cli_commands(self, *args) -> None:
        """
        Registers cli commands required for the cli commands to work.
        To register a new cli command, just pass it to arguments along with the others.

        :param '*args': the variable arguments are used to get a list of cli commands.
        """
        for command in args:
            try:
                self._app.cli.add_command(command)
            except Exception as e:
                self._app.logger.error("An error occurred while registration cli commands - {}".format(e))

    def setup_logging_error_handling(self, logs_folder=None, log_level=logging.DEBUG) -> None:
        """
        Configures the app logs and error handling systems.

        :param logs_folder: folder where log files will be stored. If None the route will be taken
            from the variable 'self.logs_folder', defaults to None
        :type logs_folder: str, optional
        :param log_level: logger level (debug, info, warning, error, exception, critical), defaults to logging.DEBUG
        """

        # Logging to the file
        path_to_logs = logs_folder if logs_folder else self.logs_folder

        if not os.path.exists(path_to_logs):
            os.mkdir(path_to_logs)

        file_handler = RotatingFileHandler(os.path.join(path_to_logs, "main.log"), maxBytes=10240, backupCount=5)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
        )

        self._app.logger.addHandler(file_handler)
        self._app.logger.setLevel(log_level)

        # Email notifications about failures
        auth = secure = None

        if self._app.config["MAIL_USERNAME"] and self._app.config["MAIL_PASSWORD"]:
            auth = (
                self._app.config["MAIL_USERNAME"],
                self._app.config["MAIL_PASSWORD"],
            )
        if self._app.config["MAIL_USE_TLS"]:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(self._app.config["MAIL_SERVER"], self._app.config["MAIL_PORT"]),
            fromaddr="no-reply@cabinet.support",
            toaddrs=self._app.config["ADMINS"],
            subject="Cabinet Error",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        self._app.logger.addHandler(mail_handler)

        # Marshmallow ValidationError
        @self._app.errorhandler(ValidationError)
        def handle_marshmallow_validation(err):
            return jsonify(err.messages), 400

    def get_flask_app(self) -> "Flask":
        """Returns an object with Flask instance"""
        return self._app

    def run(self, name) -> None:
        """
        Launches the application in debug mode BUT NOT in testing mode(using global database instead of temporary).

        :param name: the name of the file in which this function is called
        :type name: str
        """

        if name == "__main__":
            # Run the application if file was started directly ($ python name.py)
            self._app.run(debug=True)


from module.server.models import (
    user,
    payment_cards,
    jwt_tokens,
)  # these imports are required for migration
