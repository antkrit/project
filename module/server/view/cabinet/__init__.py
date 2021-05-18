"""
Init blueprint for the cabinet view.
Routes:
    /cabinet - cabinet of the user
"""
from flask import Blueprint

bp = Blueprint('cabinet', __name__)

from module.server.view.cabinet import routes
