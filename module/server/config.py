import os
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))


class Config:
    """Parent configuration class."""
    # WARNING: keep the secret key used in production secret
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')  # stores database file "app.db" by the ../module/server/ path
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    # By default is configured on the Python SMTP debugging server
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 8025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Who'll send emails
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['email@example.com']  # Who'll receive emails about failures


class TestConfig(Config):
    """Configurations for Testing, with a separate test database."""
    # If the application is tested - the database is created in the memory of the machine.
    # After working with it must be deleted (temp_db.session.remove(); temp_db.drop_all()).
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    # Can be useful if the application needs to determine if it is running in tests or not (access via app.testing).
    TESTING = True
