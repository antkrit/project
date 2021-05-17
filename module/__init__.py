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


with open((os.path.join(os.path.dirname(__file__), 'server', 'static', 'pkg_info.json'))) as info:
    _info = load(info)

__version__ = _info['version']


class App:
    """Creates and configures the flask app (Application-factory)"""

    db = SQLAlchemy()
    migrate = Migrate()
    ma = Marshmallow()
    moment = Moment()
    jwt = JWTManager()
    login_manager = LoginManager()
    login_manager.login_view = 'login.login_view'
    login_manager.session_protection = 'strong'

    def __init__(self,  testing=False, config_obj=Config):
        """
        Initializes all the components needed to run the application.

        Also sets the "before_request" decorator, which updates the lifetime of the session (5 minutes).
        To change the possible period of user inactivity - change the argument of the timedelta function.
        If this period is over, the user will be automatically redirected to the login page.

        :param testing: determines whether to create a program in test mode
        :param config_obj: custom config object
        """
        # Folders
        self.migration_folder = os.path.join(os.path.dirname(__file__), 'server', 'models', 'migrations')
        self.templates_folder = os.path.join(os.path.dirname(__file__), 'client', 'templates')
        self.static_folder = os.path.join(os.path.dirname(__file__), 'client', 'static')
        self.logs_folder = os.path.join(os.path.dirname(__file__), 'server', 'static', 'logs')

        # App
        self._app = Flask(__name__, template_folder=self.templates_folder, static_folder=self.static_folder)
        if testing:  # Choose configuration
            self._app.config.from_object(TestConfig)
        else:
            self._app.config.from_object(config_obj)
        
        App.db.init_app(self._app)
        with self._app.app_context():  # Fixing ALTER table SQLite issue
            if App.db.engine.url.drivername == 'sqlite':
                App.migrate.init_app(self._app, App.db, render_as_batch=True, directory=self.migration_folder)
            else:
                App.migrate.init_app(self._app, App.db, directory=self.migration_folder)

        App.ma.init_app(self._app)
        App.login_manager.init_app(self._app)
        App.moment.init_app(self._app)
        App.jwt.init_app(self._app)

        # Init api
        from module.server.api.resources import api
        api.init_app(self._app)

        self.setup_logging_error_handling()

        @self._app.before_request
        def before_request():
            # Updates the session time before each request to server. Sets it to 5 minutes (may be changed).
            session.permanent = True
            self._app.permanent_session_lifetime = timedelta(minutes=5)

    def register_blueprints(self, *args):
        """
        Registers blueprints required for the application routes to work.
        To register a new blueprint, just pass it to arguments along with the others.
        *args: array of blueprints
        """
        for bp in args:
            try:
                self._app.register_blueprint(bp)
            except Exception as e:
                self._app.logger.error("An error occurred while registration blueprint - {}".format(e))

    def setup_logging_error_handling(self, logs_folder=None, log_level=logging.DEBUG):
        """
        Configures the app logs and error handling systems.
        :param logs_folder: folder where log files will be stored
        :param log_level: logger level (debug, info, warning, error, exception, critical)
        """

        # Logging to the file
        path_to_logs = logs_folder if logs_folder else self.logs_folder

        if not os.path.exists(path_to_logs):
            os.mkdir(path_to_logs)

        file_handler = RotatingFileHandler(
            os.path.join(path_to_logs, 'main.log'),
            maxBytes=10240,
            backupCount=5
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )

        self._app.logger.addHandler(file_handler)
        self._app.logger.setLevel(log_level)

        # Email notifications about failures
        auth = secure = None

        if self._app.config['MAIL_USERNAME'] and self._app.config['MAIL_PASSWORD']:
            auth = (self._app.config['MAIL_USERNAME'], self._app.config['MAIL_PASSWORD'])
        if self._app.config['MAIL_USE_TLS']:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(self._app.config['MAIL_SERVER'], self._app.config['MAIL_PORT']),
            fromaddr='no-reply@cabinet.support',
            toaddrs=self._app.config['ADMINS'],
            subject='Cabinet Error',
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        self._app.logger.addHandler(mail_handler)

        # Marshmallow ValidationError
        @self._app.errorhandler(ValidationError)
        def handle_marshmallow_validation(err):
            return jsonify(err.messages), 400

    def get_flask_app(self):
        """Returns an object with Flask instance."""
        return self._app

    def run(self, name):
        """
        Launches the application in debug mode BUT NOT in testing mode(using global database instead of temporary).
        :param name: the name of the file in which this function is called
        """

        if name == '__main__':
            # Run the application with debug mode(not testing) if file was started directly ($ python file.py)
            self._app.logger.info('Website startup')
            self._app.run(debug=True)


from module.server.models import user, payment_cards, jwt_tokens  # these imports are required for migration
