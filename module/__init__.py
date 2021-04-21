"""Initializes all dependencies and creates apps"""
from datetime import timedelta
from flask import Flask, session
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from module.server.config import Config, TestConfig


class App:
    """Creates and configures the flask app (Application factory)"""

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
        self._app = Flask(__name__, template_folder='./client/templates', static_folder='./client/static')
        self._app.config.from_object(TestConfig) if testing else self._app.config.from_object(Config)

        App.db.init_app(self._app)
        App.migrate.init_app(self._app, App.db)
        App.login_manager.init_app(self._app)

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
                print("An error occurred while registration blueprint - {}".format(e))

    def get_flask_app(self):
        """Returns an object with Flask instance."""
        return self._app

    def run(self, name):
        """
        Launches the application in debug mode BUT NOT in testing mode(using global database instead of temporary).

        Also sets the decorator "before_first_request", which checks whether there are records in the database.
        If not then creates an account for the admin (account with id 1).
        To set a password for the admin, change the argument of the set_password function.
        WARNING: do not show or publish this password anywhere

        :param name: the name of the file in which this function is called
        """
        from module.server.models.user import User

        @self._app.before_first_request
        def before_first_request():
            user = User.query.first()
            if not user:
                # If the first row in the table doesn't exist
                # Creates account with login "admin" and password "test"(both fields may be changed).
                admin = User(username='admin')
                admin.set_password('test')

                # Add & save to the database
                App.db.session.add(admin)
                App.db.session.commit()

        if name == '__main__':
            # Run the application with debug mode(not testing) if file was started directly ($ python file.py).
            self._app.run(debug=True)
