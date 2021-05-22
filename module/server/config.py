"""File with different 'config' objects for the flask app"""
import os
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv


BASEDIR = os.path.abspath(os.path.dirname(__file__))  # ../module/server
load_dotenv(find_dotenv(), override=True)


class Config:
    """Parent configuration class"""

    CSRF_ENABLED = True
    PROPAGATE_EXCEPTIONS = True

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

    # WARNING: keep these keys used in production secret
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY", "dev")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev")

    # Database
    # stores database file "app.db" by the ../module/server/static/ path
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(BASEDIR, "static", "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    # By default is configured on the Python SMTP debugging server
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 8025))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", False)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")  # Who'll send emails
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["email@example.com"]  # Who'll receive emails about failures


class TestConfig(Config):
    """Configurations for Testing, with a separate test database."""

    # If the application is tested - the database is created in the memory of the machine.
    # After working with it must be deleted (temp_db.session.remove(); temp_db.drop_all()).
    SQLALCHEMY_DATABASE_URI = "sqlite://"

    # Can be useful if the application needs to determine if it is running in tests or not (access via app.testing).
    TESTING = True
    DEBUG = True
