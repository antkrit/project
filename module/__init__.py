"""Initializes all dependencies and creates apps"""
import os
import logging
from json import load
from uuid import uuid4
from datetime import timedelta
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import Flask, session
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from module.server.config import Config, TestConfig


with open(os.path.join(os.path.dirname(__file__), 'pkg_info.json')) as info:
    _info = load(info)

__version__ = _info['version']


class App:
    """Creates and configures the flask app (Application-factory)"""

    db = SQLAlchemy()
    migrate = Migrate()
    login_manager = LoginManager()
    login_manager.login_view = 'login.login_view'
    login_manager.session_protection = 'strong'

    def __init__(self,  testing=False):
        """
        Initializes all the components needed to run the application.

        Also sets the "before_request" decorator, which updates the lifetime of the session (5 minutes).
        To change the possible period of user inactivity - change the argument of the timedelta function.
        If this period is over, the user will be automatically redirected to the login page.

        :param testing: determines whether to create a program in test mode
        """
        # Folders
        self.migration_folder = os.path.join('module', 'server', 'models', 'migrations')
        self.templates_folder = os.path.join('.', 'client', 'templates')
        self.static_folder = os.path.join('.', 'client', 'static')
        self.logs_folder = os.path.join('module', 'logs')

        # App
        self._app = Flask(__name__, template_folder=self.templates_folder, static_folder=self.static_folder)
        if testing:  # Choose configuration
            self._app.config.from_object(TestConfig)
        else:
            self._app.config.from_object(Config)

        App.db.init_app(self._app)
        with self._app.app_context():  # Fixing ALTER table SQLite issue
            if App.db.engine.url.drivername == 'sqlite':
                App.migrate.init_app(self._app, App.db, render_as_batch=True, directory=self.migration_folder)
            else:
                App.migrate.init_app(self._app, App.db, directory=self.migration_folder)
        App.login_manager.init_app(self._app)

        self.setup_logging()

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

    def setup_logging(self, logs_folder=None, log_level=logging.DEBUG):
        """
        Configures the app logging system.

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

    def get_flask_app(self):
        """Returns an object with Flask instance."""
        return self._app

    @staticmethod
    def fill_test_data(user_model, card_model, tariffs, states):
        """
        Fills database tables with test data
        :param user_model: the object with which the user is created
        :param card_model: the object with which the payment card is created
        """
        # Creates two additional users with and without email
        usr1 = user_model(
            username='john',
            phone='+380991122333',
            email='example@test.com',
            tariff=tariffs.tariff_50m.value['tariff_name'],
            ip='127.0.0.1',
            address='Mazepa st. 43',
            state=states.activated_state.value,
            balance=0
        )
        usr1.set_password('test')
        App.db.session.add(usr1)

        usr2 = user_model(
            username='andre',
            phone='+380992244555',
            tariff=tariffs.tariff_50m.value['tariff_name'],
            ip='127.0.0.2',
            address='Doroshenko st. 53',
            state=states.activated_state.value,
            balance=0
        )
        usr2.set_password('test')
        App.db.session.add(usr2)

        num_200_test_cards = 5  # number of cards with amount 200
        num_400_test_cards = 6  # number of cards with amount 400

        # Creates cards with codes in range 000000-000004 and amount 200
        for i in range(num_200_test_cards):
            rand_uuid = str(uuid4())
            card = card_model(
                uuid=rand_uuid,
                amount=200,
                code=str(i).rjust(6, '0')
            )
            App.db.session.add(card)

        # Creates cards with codes in range 000005-000010 and amount 400
        for i in range(num_200_test_cards, num_200_test_cards + num_400_test_cards):
            rand_uuid = str(uuid4())
            card = card_model(
                uuid=rand_uuid,
                amount=400,
                code=str(i).rjust(6, '0')
            )
            App.db.session.add(card)

    def run(self, name):
        """
        Launches the application in debug mode BUT NOT in testing mode(using global database instead of temporary).

        Also sets the decorator "before_first_request", which checks whether there are records in the database.
        If not then creates an account for the admin (account with id 1).
        To set a password for the admin, change the argument of the set_password function.
        WARNING: do not show or publish this password anywhere

        :param name: the name of the file in which this function is called
        """
        from module.server.models import user, payment_cards  # These imports are also required for migration

        user_model = user.User
        card_model = payment_cards.Card
        tariffs = user.Tariffs
        states = user.State

        @self._app.before_first_request
        def before_first_request():
            usr = user_model.query.first()
            if not usr:
                # If the first row in the table doesn't exist
                # Creates account with login "admin" and password "test"(both fields may be changed).
                admin = user_model(username='admin')
                admin.set_password('test')
                App.db.session.add(admin)

                # Fill the database with test data
                App.fill_test_data(user_model, card_model, tariffs, states)

                # Commit changes
                App.db.session.commit()

        if name == '__main__':
            # Run the application with debug mode(not testing) if file was started directly ($ python file.py).
            self._app.run(debug=True)
