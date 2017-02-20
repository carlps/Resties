# project/places/views.py

###############
### imports ###
###############

from functools import wraps
from flask import (flash, redirect, render_template, 
				  request, session, url_for, Blueprint, abort)

from project import db
from project.models import Place, GooglePlace, Visit
from .forms import VisitForm, NotesForm

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
	''' get the list of places for logged in user'''

	# should filter to where user id id logged in user ID
	if 'logged_in' not in session:
		userID = 1 # placeholder for now
	else: 
		userID = session['userID']
	return db.session.query(Place).filter_by(userID=userID)

def getPlace(placeID, userID):
	'''get single place object for given placeID and userID'''
	return db.session.query(Place).filter_by(placeID=placeID,userID=userID).first()

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
@login_required
def details(placeID):
	place = GooglePlace(placeID)
	if 'logged_in' in session:
		notes = db.session.query(Place).filter_by(placeID=placeID,userID=session['userID']).first().notes
	else:
		notes = None
	return render_template( 
		#note: template uses unique api key only for displaying maps
		#when migrating to prod, restrict to only traffic from website 
		'details.html',
		place=place,
		notes=notes,
		visits=getVisits(placeID)
	)

@places_blueprint.route('/addVisit/<string:placeID>', methods=['GET','POST'])
@login_required
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

@places_blueprint.route('/editNotes/<string:placeID>', methods=['GET','POST'])
@login_required
def editNotes(placeID):
	'''temporary until I figure out how to javascript it in the details page'''
	error = None
	place = getPlace(placeID,session['userID'])
	form = NotesForm(request.form)
	if request.method == 'POST':
		place.notes = form.notes.data
		db.session.commit()
		flash('Notes updated!')
		return redirect(url_for('places.details', placeID=placeID)) 
	return render_template('editNotes.html', place=place, error=error, form=form)


###############################################################################
#################################### TODO #####################################
###############################################################################
### clean up home page. make it easier to find restie on your list			###
###	--did a lot, but could do more											###
###																			###
### allow people to edit notes on places page								###
###	--temp workaround is editNotes page. need JS for in page				###
### --also having a date auto pop'd when a note is added. 
### --maybe like a table
###																			###
### have a search for places and add them to db								###
###	--will have to have a geolocate in search								###
###																			###
###																			###
###	maps widget in place details											###
###																			###
###############################################################################
###############################################################################
###############################################################################