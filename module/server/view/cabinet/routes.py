"""Define the route of the user cabinet"""
from flask import render_template
from flask_login import login_required

from module.server.view.cabinet import bp


@bp.route('/cabinet', methods=['GET', 'POST'])
@login_required
def cabinet_view():
    """
    View for the cabinet page.
    After the user has successfully entered his login and password, he passes into his cabinet.
    If the user tries to enter this route without logging in, he will be automatically redirected to the login page.

    Methods: GET, POST
    """

    return render_template('cabinet/cabinet.html')
