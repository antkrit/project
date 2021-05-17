"""
Init blueprint for the admin view.
Routes:
    {website_url}/admin/ - admin cabinet
    {website_url}/admin/register - register view
"""
from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

from module.server.view.admin import routes
