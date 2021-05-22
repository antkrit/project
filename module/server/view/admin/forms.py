"""Forms that are required for the admin interface"""
from re import compile
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from module.server.models.user import User


class SearchUserForm(FlaskForm):
    """
    Searching for a user by username.
    Fields: username - login of the user.
    Buttons: search_button - sends data from field to the server for processing.
    """

    username = StringField("Username", validators=[Length(3, 64)])
    search_button = SubmitField("Search")


class InteractButtonsForm(FlaskForm):
    """
    Interaction with user account.
    Buttons: register_button - register a new user, activate_button - set "activated" status to the account,
    deactivate_button - set "deactivated" status to the account, delete_button - delete user from the database.
    """

    register_button = SubmitField("Register")
    activate_button = SubmitField("Activate")
    deactivate_button = SubmitField("Deactivate")
    delete_button = SubmitField("Delete")


class RegisterForm(FlaskForm):
    """
    Register new user account.
    Fields: username - future user login, email - future user email, phone - phone number,
    name - full name, tariff_select - selector that determines what the user's tariff will be,
    password, repeat_password - future user password (must be equal).
    Buttons: submit - sends data from fields to the server for processing.
    """

    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3)],
        render_kw={"placeholder": "*Username"},
    )
    email = StringField("Email", render_kw={"placeholder": "Email"}, filters=[lambda x: x or None])
    phone = StringField("Phone", validators=[DataRequired()], render_kw={"placeholder": "*Phone"})
    name = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "*Full name"})
    address = StringField("Address", validators=[DataRequired()], render_kw={"placeholder": "*Address"})
    tariff_select = SelectField("Tariff", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=4)],
        render_kw={"placeholder": "*Password", "autocomplete": "off"},
    )
    repeat_password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match\n"),
        ],
        render_kw={"placeholder": "*Repeat password", "autocomplete": "off"},
    )
    submit = SubmitField("Register", render_kw={"class": "btn"})

    def validate_username(self, username):
        """
        Validate Username field. Checks if there is a row with such an username and if it's match pattern
        :param username: username from the field
        :type username: str
        :raises ValidationError: if username already exists in the database or it doesn't match pattern
        """
        username_pattern = compile(r"^[A-Za-z0-9]+$")

        if not username_pattern.findall(self.username.data):
            raise ValidationError("Username is not correct.")

        if User.query.filter_by(username=self.username.data).first():
            raise ValidationError("This username already exists.")

    def validate_phone(self, phone):
        """
        Validate Phone field. Checks if there is a row with such a phone number and if it's match pattern.
        :param phone: phone number from the field
        :type phone: str
        :raises ValidationError: if phone number already exists in the database or it doesn't match pattern
        """
        phone_pattern = compile(r"^[+0-9]{10,13}$")

        if not phone_pattern.findall(self.phone.data):
            raise ValidationError("Phone number is not correct.")

        if User.query.filter_by(phone=self.phone.data).first():
            raise ValidationError("This phone already exists.")

    def validate_email(self, email):
        """
        Validate Email field. Allows empty field and checks if it's match pattern.
        :param email: email from the field
        :type email: str
        :raises ValidationError: if email doesn't match pattern
        """
        email_pattern = compile(r"^[a-zA-Z0-9]+[@][a-z]+\.[a-z]+$")

        if self.email.data and not email_pattern.findall(self.email.data):
            raise ValidationError("Email address is not correct.")
