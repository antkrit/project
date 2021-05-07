"""Define the route of the user cabinet"""
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from module.server.view.cabinet import bp, forms as f


@bp.route('/cabinet', methods=['GET', 'POST'])
@login_required
def cabinet_view():
    """
    View for the cabinet page.
    After the user has successfully entered his login and password, he passes into his cabinet.
    If the user tries to enter this route without logging in, he will be automatically redirected to the login page.
    Methods: GET, POST
    """
    if current_user.username == 'admin':  # If current user is admin redirect him to the admin interface
        return redirect(url_for('admin.admin_view'))

    payment_card_form = f.PaymentCardForm()
    if payment_card_form.validate_on_submit() or request.method == 'POST':  # if user clicked the "Enter" button
        current_user.use_card(card_code=payment_card_form.code.data)

    return render_template(
        'cabinet/cabinet.html',
        user_info=current_user.get_info(),
        user_history=current_user.get_history()[:10],
        title='Cabinet',
        form=payment_card_form
    )
