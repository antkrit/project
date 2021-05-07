"""Define the route of the login form"""
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from module.server.view.admin import bp
from module.server.models.user import User
from module.server.models.payment_cards import Card


@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_view():
    """
    View for the admin page.
    Access only for user with nickname 'admin'.
    If the user tries to enter this route without logging in, he will be automatically redirected to the login page.
    Methods: GET, POST
    """
    if current_user.username != 'admin':  # If current user is not admin redirect him to the cabinet
        return redirect(url_for('admin.admin_view'))

    # Data for the table with main info
    data_general_table = dict(
        num_users=len(User.query.all()),
        num_active_users=len(User.query.filter_by(state='activated').all()),
        num_non_used_cards=len(Card.query.all()),
        total_debt=sum(debt_acc.balance for debt_acc in User.query.filter(User.balance < 0).all()),
    )

    return render_template('admin/admin.html', title='Admin', data_general_table=data_general_table)
