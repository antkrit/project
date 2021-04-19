"""Initializes all dependencies and creates apps"""
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def create_app(test_config: dict = None) -> Flask:
    """Creates and configures the flask app"""

    curr_app = Flask(__name__)
    curr_app.config.from_pyfile('config.py', silent=True)
    if test_config and isinstance(test_config, dict):
        # load the test config
        curr_app.config.from_mapping(test_config)

    db.init_app(curr_app)
    migrate.init_app(curr_app, db)

    return curr_app


from app.models import user
