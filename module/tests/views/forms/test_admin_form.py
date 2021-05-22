"""Test forms from admin view"""
from wtforms.validators import ValidationError
from module.tests import init_app
from module.server.view.admin.forms import RegisterForm


def test_validation(init_app):
    """Checks whether field data can be validated correctly"""
    app = init_app

    with app.test_request_context():
        form = RegisterForm()

        # Username validation
        try:
            form.username.data = "asd*"
            form.validate_username("asd*")
            assert False
        except ValidationError:  # if validation error was raised - everything is okay
            assert True

        try:
            form.username.data = "asd"
            form.validate_username("asd")
            assert True
        except ValidationError:  # if validation error was raised - something goes wrong
            assert False

        # Phone validation
        try:
            form.phone.data = "123"
            form.validate_phone("123")
            assert False
        except ValidationError:  # if validation error was raised - everything is okay
            assert True

        try:
            form.phone.data = "+380991122333"
            form.validate_phone("+380991122333")
            assert True
        except ValidationError:  # if validation error was raised - something goes wrong
            assert False

        # Email validation
        try:
            form.email.data = "asd1"
            form.validate_email("asd1")
            assert False
        except ValidationError:  # if validation error was raised - everything is okay
            assert True

        try:
            form.email.data = "asd@test.com"
            form.validate_email("asd@test.com")
            assert True
        except ValidationError:  # if validation error was raised - something goes wrong
            assert False
