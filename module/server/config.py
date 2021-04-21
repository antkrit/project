import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # WARNING: keep the secret key used in production secret
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')  # stores database file "app.db" by the ../module/server/ path
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    # If the application is tested - the database is created in the memory of the machine.
    # After working with it must be deleted (temp_db.session.remove(); temp_db.drop_all()).
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    # Can be useful if the application needs to determine if it is running in tests or not (access via app.testing).
    TESTING = True
