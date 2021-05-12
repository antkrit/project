"""
Init blueprint for the admin view.
Routes:
    {website_url}/admin - admin cabinet
"""
from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

from module.server.view.admin import routes
