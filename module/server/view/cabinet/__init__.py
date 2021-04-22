"""
Init blueprint for the cabinet view.
Routes:
    {website_url}/cabinet - cabinet of the user
"""
from flask import Blueprint

bp = Blueprint('cabinet', __name__)

from module.server.view.cabinet import routes
