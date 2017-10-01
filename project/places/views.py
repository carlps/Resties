# project/places/views.py

###############
### imports ###
###############

from functools import wraps
from os import environ
from datetime import date
import requests

from flask import (flash, redirect, render_template,
				  request, session, url_for, Blueprint, abort)
from sqlalchemy.exc import IntegrityError

from project import db
from project.models import Place, GooglePlace, Visit, ZipCode, User, UserPlace
from .forms import VisitForm, NotesForm, SearchForm
from project.utils.zipUtils import zipCheck

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


def getUserPlaces():
	''' get the list of places for logged in user'''

	# should filter to where user id id logged in user ID
	if 'logged_in' not in session:
		userID = 1  # placeholder for now
	else:
		userID = session['userID']
	# want to return Places, filtered by UserPlace where userID
	return db.session.query(Place).\
			join(Place.userPlaces).\
			filter(UserPlace.userID==userID)


def getUserPlace(placeID, userID):
	'''get single userPlace object for given placeID and userID'''
	return db.session.query(UserPlace).filter_by(placeID=placeID, userID=userID).first()


def getVisits(placeID):
	if 'logged_in' not in session:
		return None
	else:
		userID = session['userID']
		return db.session.query(Visit).filter_by(userID=userID, placeID=placeID)


def getUserZip():
	return db.session.query(User).filter_by(userID=session['userID']).first().zipCode


def getLatLngFromZip(zipCode):
	zipCheck(zipCode)
	return db.session.query(ZipCode).filter_by(zipCode=zipCode).with_entities(
		ZipCode.latitude, ZipCode.longitude).first()


def searchForPlace(searchTerm, **kwargs):

	if 'zipCode' in kwargs:
		zipCode = kwargs['zipCode']
		print(f'set zipcode to {zipCode}')
	else:
		print("didn't supply zip, so getting from user profile")
		zipCode = getUserZip()
	if 'radius' in kwargs:
		radius = kwargs['radius']
	else:
		# default to 20000
		radius = 20000

	# get lat and lng info from zip code table
	lat, lng = getLatLngFromZip(zipCode)
	# generate search url
	url = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
		'location={lat},{lng}&radius={radius}&'
		'type=food&keyword={keyword}&key={key}').format(
			lat=lat,
			lng=lng,
			radius=radius,
			keyword=searchTerm,
			key=environ['GOOGLE_API_RESTIES']
		)
	# use requests to lookup place
	print(url)
	request = requests.get(url)
	# ensure valid response
	if request.status_code != 200:
		raise AttributeError('Request returned bad response')

	# if valid response, return results from json response
	results = request.json()['results']

	# create empty list to hold places
	places = []
	# since search can (and most likely will) return multiple,
	# iterate through and create Google Places out of them
	# and append to places list
	for result in results:
		# GooglePlace neeeds id and result
		newPlace = GooglePlace(result['place_id'], result)
		# filter out anywhere permanently closed
		# maybe keep and notify instead?
		# check if place already in user's list
		# if so, replace key with

		if db.session.query(UserPlace).filter_by(placeID=result['place_id'], userID=session['userID']).first():
			newPlace.inList = True

		if not newPlace.permanently_closed:
			places.append(newPlace)

	return places


def addPlaceToUserList(placeID):
	''' Insert a place into the database for a user.
	First ensures that the place is in database. Then,
	Creates a new UserPlace record and adds it to the
	database.'''

	# ensure Place is in DB
	newPlace = tryPlace(placeID)
	newUserPlace = UserPlace(session['userID'], placeID)
	db.session.add(newUserPlace)
	db.session.commit()
	return newPlace


def tryPlace(placeID):
	''' Checks if a place is already in DB 
	If it is not, it inserts. If it is, does nothing.
	Returns Place object'''
	place = db.session.query(Place).filter_by(placeID=placeID).first()
	if not place:
		# kind of inefficient to take only ID and create full Google Place
		# just to get name. Should update in future to take ID and name
		googlePlace = GooglePlace(placeID)
		place = Place(placeID, googlePlace.name)
		db.session.add(place)
		db.session.commit()
	return place


def milesToMeters(miles):
	return int(int(miles)*1609.34)

##############
### routes ###
##############

@places_blueprint.route('/')
def userPlaces():
	return render_template(
		'userPlaces.html',
		places=getUserPlaces()
	)

@login_required
@places_blueprint.route('/search', methods=['GET','POST'])
def search():
	zipCode = getUserZip()
	radius = 12
	form = SearchForm(zipCode,radius)
	if request.method == 'POST':
		searchTerm = request.form['searchTerm'].replace(' ','+')
		zipCode = request.form['zipCode']
		radius = milesToMeters(request.form['radius'])
		return render_template(
			'results.html',
			places = searchForPlace(searchTerm=searchTerm,
									zipCode=zipCode,
									radius=radius),
			searchTerm = searchTerm,
			searchTermLookup = searchTerm,
			key=environ['GOOGLE_API_RESTIES'],
			zipCode=zipCode
			)

	return render_template('search.html',form=form)



@places_blueprint.route('/addPlace/<string:placeID>', methods=['POST'])
@login_required
def addPlace(placeID):
	# since GET is not in methods, if GET is attempted, 405 will be returned
	# a bit inefficient since we have the google place details in the search
	# and we only send the ID and create a new google place out of it just to
	# get the name when adding to DB. update in the future.
	try:
		newPlace = addPlaceToUserList(placeID)
		flash('{} is added to your list!'.format(newPlace.placeName))
		return redirect(url_for('places.details', placeID=newPlace.placeID))
	except IntegrityError:
		# hopefully should never get here due to front end logic
		# which doesn't render an add button for a place already
		# in the users list
		error = 'That place is already in this users list.'
		# user query string should be saved and then used here instead of place.name
		return render_template('places.results', searchTerm=newPlace.placeName, error=error)

@places_blueprint.route('/details/<string:placeID>')
@login_required
def details(placeID):
	place = GooglePlace(placeID)
	if 'logged_in' in session:
		notes = db.session.query(UserPlace).filter_by(
		    placeID=placeID,userID=session['userID']).first().notes
	else:
		notes = None

	# add a button to edit each visit.
	return render_template(
		# note: template uses unique api key only for displaying maps
		# when migrating to prod, restrict to only traffic from website
		'details.html',
		place=place,
		notes=notes,
		visits=getVisits(placeID),
		key=environ['GOOGLE_API_RESTIES']
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

@places_blueprint.route('/editVisit/<string:visitID>', methods=['GET','POST'])
@login_required
def editVisit(visitID):
	visit = db.session.query(Visit).filter_by(
	    userID=session['userID'],visitID=visitID).first()
	print(visitID)
	place = GooglePlace(visit.placeID)
	error = None
	form = VisitForm(request.form, visitDate=visit.visitDate)
	if request.method == 'POST':
		if form.validate_on_submit():
			print(visit.visitID)
			visit.visitDate = form.visitDate.data
			visit.comments = form.comments.data
			db.session.commit()
			flash('Visit updated!')
			return redirect(url_for('places.details', placeID=visit.placeID))
	return render_template('addVisit.html', form=form,
							error=error, place=place, visit=visit)


@places_blueprint.route('/editNotes/<string:placeID>', methods=['GET','POST'])
@login_required
def editNotes(placeID):
	'''temporary until I figure out how to javascript it in the details page'''
	error = None
	place = getUserPlace(placeID,session['userID'])
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
# --also having a date auto pop'd when a note is added. 
# --maybe like a table
###																			###
### have a search for places and add them to db								###
###	--will have to have a geolocate in search								###
###	--or better, just have a zip for user									###
###	----have zips now														###
###																			###
### search bar in header													###
### --returns places in list (if found)										###
### --and wider search														###
### --or maybe have a radio button?											###
###																			###
###	maps widget in place details											###
###	--done with iframe														###
###	--maybe look into js?													###
###	--also NOTE: created new api creds for only map rendering				###
###	----need to restrict to my website when prod							###
###																			###
###																			###
###############################################################################
###############################################################################
###############################################################################
