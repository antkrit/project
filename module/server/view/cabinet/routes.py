"""Define the route of the user cabinet"""
from flask import render_template, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from module.server.view.cabinet import bp, forms as f


@bp.route("/cabinet", methods=["GET", "POST"])
@login_required
def cabinet_view():
    """
    View for the cabinet page.
    After the user has successfully entered his login and password, he passes into his cabinet.
    If the user tries to enter this route without logging in, he will be automatically redirected to the login page.
    Methods: GET, POST
    """
    if current_user.username == "admin":  # If current user is admin redirect him to the admin interface
        return redirect(url_for("admin.admin_view"))

    payment_card_form = f.PaymentCardForm()
    if request.method == "POST":
        data = request.form
        if payment_card_form.validate_on_submit() or (data and current_app.testing):
            # if user clicked the "Enter" button or there is data in the request while testing app
            current_user.use_card(card_code=data.get("code"))

    return render_template(
        "cabinet/cabinet.html",
        user_info=current_user.get_info(),
        user_history=current_user.get_history(),
        title="Cabinet",
        form=payment_card_form,
    )
