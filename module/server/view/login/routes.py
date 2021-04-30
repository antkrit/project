"""Define the route of the login form"""
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user

from module.server.models.user import User
from module.server.view.login import bp, forms as f


@bp.route('/', methods=['GET', 'POST'])
def login_view():
    """
    View for the login page.
    Once the user tries to get to his account, he will be redirected to the login page.

    Methods: GET, POST
    """
    if current_user.is_authenticated:
        # if the user is already logged in - redirect to his cabinet
        return redirect(url_for('cabinet.cabinet_view'))

    form = f.LoginForm()
    if form.validate_on_submit() or request.method == 'POST':
        # If the user clicked the "Sign In" button
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            # If such a login exists, login and password match
            login_user(user)

            if user.username == 'admin':
                return redirect(url_for('admin.admin_view'))
            return redirect(url_for('cabinet.cabinet_view'))
        return redirect(url_for('login.login_view'))
    return render_template('auth/login.html', form=form)


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Log out current user"""
    logout_user()
    return redirect(url_for('login.login_view'))
