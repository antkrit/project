"""
Init blueprint for the login view.
Routes:
    {website_url}/ - login form
"""
from flask import Blueprint

bp = Blueprint('login', __name__)

from module.server.view.login import routes
