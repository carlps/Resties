# project/places/views.py

###############
### imports ###
###############

from functools import wraps
from flask import (flash, redirect, render_template, 
				  request, session, url_for, Blueprint, abort)

from project import db
from project.models import Place, GooglePlace, Visit
from .forms import VisitForm

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
	def wrap(*args, **kwargs):
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

@places_blueprint.route('/addVisit/<string:placeID>', methods=['GET','POST'])
#@login_required
def addVisit(placeID):
	error = None
	place = GooglePlace(placeID)
	form = VisitForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			newVisit = Visit(
				form.visitDate.data,
				form.comments.data,
				session['userID'],
				placeID
			)
			db.session.add(newVisit)
			db.session.commit()
			flash('Visit recorded! I hope you enjoyed!')
			return redirect(url_for('places.details', placeID=placeID))
	return render_template('addVisit.html', form=form, error=error, place=place)


###############################################################################
#################################### TODO #####################################
###############################################################################
### clean up home page. make it easier to find restie on your list			###
### allow people to edit notes on places page								###
### have a search for places and add them to db								###
###																			###
###############################################################################
###############################################################################
###############################################################################