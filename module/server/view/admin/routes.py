"""Define the route of the login form"""
from flask import render_template
from module.server.view.admin import bp


@bp.route('/admin', methods=['GET', 'POST'])
def admin_view():
    return render_template('admin/admin.html')
