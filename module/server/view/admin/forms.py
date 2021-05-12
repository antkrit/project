"""Forms that are required for admin interface"""
from re import compile
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError


class SearchUserForm(FlaskForm):
    """
    Searching for a user by username.
    Fields: username - login of the user.
    Buttons: search_button - sends data from field to the server for processing.
    """
    username = StringField(
        'Username',
        validators=[Length(3, 64)]
    )
    search_button = SubmitField('Search')


class InteractButtonsForm(FlaskForm):
    """
    Interaction with user account.
    Buttons: register_button - register a new user, activate_button - set "activated" status to the account,
    deactivate_button - set "deactivated" status to the account, delete_button - delete user from the database.
    """
    register_button = SubmitField('Register')
    activate_button = SubmitField('Activate')
    deactivate_button = SubmitField('Deactivate')
    delete_button = SubmitField('Delete')


class RegisterForm(FlaskForm):
    """
    Register new user account.
    Fields: username - future user login, email - future user email, phone - phone number,
    name - full name, tariff_select - selector that determines what the user's tariff will be,
    password, repeat_password - future user password (must be equal).
    Buttons: submit - sends data from fields to the server for processing.
    """
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3)],
        render_kw={'class': 'input-field', 'placeholder': '*Username'}
    )
    email = StringField(
        'Email',
        render_kw={'class': 'input-field', 'placeholder': 'Email'},
        filters=[lambda x: x or None]
    )
    phone = StringField(
        'Phone',
        validators=[DataRequired()],
        render_kw={'class': 'input-field', 'placeholder': '*Phone'}
    )
    name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={'class': 'input-field', 'placeholder': '*Full name'}
    )
    address = StringField(
        'Address',
        validators=[DataRequired()],
        render_kw={'class': 'input-field', 'placeholder': '*Address'}
    )
    tariff_select = SelectField(
        'Tariff',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=4), EqualTo('repeat_password', message='Passwords must match')],
        render_kw={'class': 'input-field', 'placeholder': '*Password', 'autocomplete': 'off'}
    )
    repeat_password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={'class': 'input-field', 'placeholder': '*Repeat password', 'autocomplete': 'off'}
    )
    submit = SubmitField('Register', render_kw={'class': 'btn'})

    def validate_email(self, email):
        """Validate Email field (Allows empty field)"""
        email_pattern = compile(r"^[a-zA-Z0-9]+[@][a-z]+\.[a-z]+$")

        if self.email.data and not email_pattern.findall(self.email.data):
            raise ValidationError('Email address is not correct.')



