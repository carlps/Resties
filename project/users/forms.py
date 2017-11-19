# project/users/forms.py

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms.validators import Email, ValidationError


def zipCheck(form, field):
    '''ensure zip code is numeric'''
    if not field.data.isnumeric():
        raise ValidationError('Zip code can only be numeric values')


class RegisterForm(Form):
    userName = StringField(
        'Username',
        validators=[DataRequired()]
    )
    fname = StringField('First Name')
    lname = StringField('Last Name')
    zipCode = StringField(
        'Zip Code',
        validators=[DataRequired(),
                    Length(min=5, max=5,
                           message='Zip Code must be exactly 5 digits'),
                    zipCheck]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm = PasswordField(
        'Repeat Password',
        validators=[DataRequired(),
                    EqualTo('password', message="Passwords didn't match.")]
    )


class LoginForm(Form):
    userName = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
