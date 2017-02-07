# project/places/forms.py

from flask_wtf import Form
from wtforms import StringField, DateField
from wtforms.validators import DataRequired
from datetime import date

class VisitForm(Form):
	visitDate = DateField(
        'Visit Date (mm/dd/yyyy)',
        validators=[DataRequired()], format='%m/%d/%Y'

	)
	comments = StringField(
		'Comments'
	)

class NotesForm(Form):
	notes = StringField(
		'Notes'
	)