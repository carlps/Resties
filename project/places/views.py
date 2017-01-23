# project/places/views.py

###############
### imports ###
###############

from functools import wraps
from flask import (flash, redirect, render_template, 
				  request, session, url_for, Blueprint)

from project import db
from project.models import Place, GooglePlace

##############
### config ###
##############

places_blueprint = Blueprint('places', __name__)

########################
### helper functions ###
########################

def login_required(test):
	'''wrapper function to test a method
	test is whether or not the user is logged in
	if logged in: allow, else: redirect'''
	@wraps(test)
	def wrap(*arg, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('users.login'))
	return wrap

def getPlaces():
	# should filter to where user id id logged in user ID
	return db.session.query(Place).order_by(Place.placeName.desc())

##############
### routes ###
##############

@places_blueprint.route('/', methods=['GET','POST'])
def places():
	return render_template(
		'places.html',
		places=getPlaces()
	)
@places_blueprint.route('/details/<string:placeID>')
def details(placeID):
	place = GooglePlace(placeID)
	print(place.formatted_address)
	return render_template(
		'details.html',
		place=place
	)

# have a search for places and add them to db