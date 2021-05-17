"""Define the route of the login form"""
from flask import render_template, redirect, url_for, request, current_app, session, flash
from flask_login import current_user, login_user, logout_user

from module.server import messages
from module.server.models.user import User
from module.server.view.login import bp, forms as f


@bp.route('/', methods=['GET', 'POST'])
def login_view():
    """
    View for the login page.
    Once the user tries to get to his account, he will be redirected to the login page.
    Methods: GET, POST
    """
    if current_user.is_authenticated:  # if the user is already logged in - redirect to his cabinet
        if current_user.username == 'admin':  # If current user is admin
            return redirect(url_for('admin.admin_view'))
        return redirect(url_for('cabinet.cabinet_view'))

    login_form = f.LoginForm()
    if request.method == "POST":
        data = request.form

        if login_form.validate_on_submit() or (data and current_app.testing):
            # If user clicked the "Sign In" button or there is data in the request while testing app
            username = data.get('username')
            password = data.get('password')

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):  # If such login exists, login and password match
                session.clear()
                login_user(user)
                flash(messages["success_login"], "info")

                if user.username == 'admin':  # If user is admin
                    return redirect(url_for('admin.admin_view'))
                return redirect(url_for('cabinet.cabinet_view'))
            return redirect(url_for('login.login_view'))
    return render_template('auth/login.html', title='Login', form=login_form)


@bp.route('/logout', methods=['GET'])
def logout():
    """
    Log out current user.
    Methods: GET
    """
    logout_user()
    return redirect(url_for('login.login_view'))
