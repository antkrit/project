"""The general configuration file of the flask app"""
import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(BASEDIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
