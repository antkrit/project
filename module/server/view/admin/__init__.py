"""
Init blueprint for the admin view.
Routes:
    /admin/ - admin cabinet
    /admin/register - register form
"""
from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

from module.server.view.admin import routes
