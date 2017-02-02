# project/places/views.py

###############
### imports ###
###############

from functools import wraps
from flask import (flash, redirect, render_template, 
				  request, session, url_for, Blueprint, abort)

from project import db
from project.models import Place, GooglePlace, Visit

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
	if 'logged_in' not in session:
		userID = 1 # placeholder for now
	else: 
		userID = session['userID']
	return db.session.query(Place).filter_by(userID=userID).order_by(Place.placeName.desc())

def getVisits(placeID):
	if 'logged_in' not in session:
		return None
	else:
		userID = session['userID']
		return db.session.query(Visit).filter_by(userID=userID,placeID=placeID)

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
	if 'logged_in' in session:
		notes = db.session.query(Place).filter_by(placeID=placeID,userID=session['userID']).first().notes
	else:
		notes = None
	return render_template(
		'details.html',
		place=place,
		notes=notes,
		visits=getVisits(placeID)
	)

# have a search for places and add them to db