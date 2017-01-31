# project/users/forms.py

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class RegisterForm(Form):
	name = StringField(
		'Username',
		validators=[DataRequired()]
	)
	email = StringField(
		'Email',
		validators=[DataRequired(), Email()]
	)
	password = PasswordField(
		'Password',
		validators=[DataRequired(),Length(min=6)]
	)
	confirm=PasswordField(
		'Repeat Password',
		validators=[DataRequired(),EqualTo('password')]
	)

class LoginForm(Form):
	name = StringField(
		'Username',
		validators=[DataRequired()]
	)
	password = PasswordField(
		'Password',
		validators=[DataRequired()]
	)