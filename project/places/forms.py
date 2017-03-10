# project/places/forms.py

from flask_wtf import Form
from wtforms import TextAreaField, StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from datetime import date

class VisitForm(Form):
	visitDate = DateField('Visit Date',
        validators=[DataRequired()], format='%d %B, %Y')

	comments = TextAreaField('Comments')

class NotesForm(Form):
	notes = TextAreaField(
		'Notes'
	)

class SearchForm(Form):
	searchTerm = StringField('Search')