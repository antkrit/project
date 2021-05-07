"""Forms that are required for login.html template"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """
    User login form.

    Fields: username - login of the user, password - password of the user
    Buttons: submit - sends data from fields to the server for processing
    """
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(1, 64)],
        render_kw={'class': 'login__input', 'placeholder': 'Username'}
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={'class': 'login__input', 'placeholder': 'Password', 'autocomplete': 'off'}
    )
    submit = SubmitField('Sign In', render_kw={'class': 'btn'})
