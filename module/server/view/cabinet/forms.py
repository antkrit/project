"""Forms that are required for cabinet.html template"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class PaymentCardForm(FlaskForm):
    """
    Payment card use form.

    Fields: username - login of the user, password - password of the user
    Buttons: submit - sends data from fields to the server for processing
    """
    code = StringField(
        'Code',
        validators=[DataRequired(), Length(1, 64)],
        render_kw={'class': 'login__input'}
    )
    submit = SubmitField('Enter', render_kw={'class': 'btn'})
