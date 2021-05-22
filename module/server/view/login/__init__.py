"""
Init blueprint for the login view.
Routes:
    / - login form
"""
from flask import Blueprint

bp = Blueprint("login", __name__)

from module.server.view.login import routes
