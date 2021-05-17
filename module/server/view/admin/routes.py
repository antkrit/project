"""Define the route to the admin interface"""
from uuid import uuid4
from flask import render_template, redirect, url_for, request, session, current_app, flash
from flask_login import login_required, current_user
from module.server import messages
from module.server.view.admin import bp
from module.server.view.admin.forms import SearchUserForm, InteractButtonsForm, RegisterForm
from module.server.models.user import User, Tariffs, State
from module.server.models.payment_cards import Card


@bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_view():
    """
    View for the admin page.
    Access only for user with nickname 'admin'.
    If the user tries to enter this route without logging in, he will be automatically redirected to the cabinet page.
    Methods: GET, POST
    """
    if current_user.username != 'admin':  # If current user is not admin redirect him to the cabinet
        return redirect(url_for('cabinet.cabinet_view'))

    search_form = SearchUserForm()
    interact_form = InteractButtonsForm()  # activate, deactivate, delete and register buttons

    if request.method == "POST":  # if any button was pressed
        data = request.form
        if data.get('search_button'):
            # if search button was pressed "remember" the username to work with in the future
            session['_username_search_form'] = data.get('username')
        elif data.get('register_button'):  # if register button was pressed
            return redirect(url_for('admin.register_view'))
        elif data.get('activate_button'):  # if activate button was pressed
            user = User.query.filter_by(username=session.get('_username_search_form')).first()
            user.change_state()
            flash(messages['activate_state_success'], "info")
        elif data.get('deactivate_button'):  # if deactivate button was pressed
            user = User.query.filter_by(username=session.get('_username_search_form')).first()
            user.change_state(deactivate=True)
            flash(messages['deactivate_state_success'], "info")
        elif data.get('delete_button'):  # if delete button was pressed
            user = User.query.filter_by(username=session.get('_username_search_form')).first()
            user.delete_from_db()
            flash(messages['success'], "info")

    # Data for the table with main info
    data_general_table = dict(
        num_users=len(User.query.all()),
        num_active_users=len(User.query.filter_by(state=State.activated_state.value).all()),
        num_non_used_cards=len(Card.query.all()),
        total_debt=sum(debt_acc.balance for debt_acc in User.query.filter(User.balance < 0).all()),
    )

    return render_template(
        'admin/admin.html',
        title='Admin',
        data_general_table=data_general_table,
        search_form=search_form,
        interact_form=interact_form,
        user=User.query.filter_by(username=session.get('_username_search_form')).first()
    )


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register_view():
    """
    New user registration view.
    Access only for user with nickname 'admin'.
    If the user tries to enter this route without logging in, he will be automatically redirected to the cabinet page.
    Methods: GET, POST
    """
    if current_user.username != 'admin':  # If current user is not admin redirect him to the cabinet
        return redirect(url_for('cabinet.cabinet_view'))

    register_form = RegisterForm()
    # Set selector options
    register_form.tariff_select.choices = [tariff.value['tariff_name'] for tariff in list(Tariffs)]

    if request.method == 'POST':
        data = request.form
        if register_form.validate_on_submit() or (data and current_app.testing):
            new_user = User(
                name=data.get('name'),
                phone=data.get('phone'),
                email=data.get('email'),
                username=data.get('username'),
                password=data.get('password'),
                tariff=data.get('tariff_select'),
                address=data.get('address'),
                state=State.activated_state.value
            )

            try:
                new_user.save_to_db()
                flash(messages['success_register'], "info")
                return redirect(url_for('admin.admin_view'))
            except ValueError as e:  # error saving to the database
                current_app.logger.info("Error while saving new user to the database - {0}".format(e))
                flash(messages['failure'], "warning")
                return redirect(url_for('admin.register_view'))

    return render_template(
        'auth/register.html',
        title='Register new user',
        form=register_form
    )
