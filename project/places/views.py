# project/places/views.py

###############
### imports ###
###############

from functools import wraps
from flask import (flash, redirect, render_template, 
				  request, session, url_for, Blueprint, abort)

from project import db
from project.models import Place, GooglePlace, Visit, ZipCode, User
from .forms import VisitForm, NotesForm, SearchForm
from os import environ
import requests

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

def searchForPlace(searchTerm):
	# get user zip code
	zipCode = db.session.query(User).filter_by(userID=session['userID']).first().zipCode
	# get lat and lng info from zip code table
	lat,lng = db.session.query(ZipCode).filter_by(zipCode=zipCode).with_entities(
		ZipCode.latitude, ZipCode.longitude).first()
	# generate search url
	url = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
		'location={lat},{lng}&radius={radius}&'
		'type=food&keyword={keyword}&key={key}').format(
			lat=lat,
			lng=lng,
			radius='20000', # default for now, add customize option later
			keyword=searchTerm,
			key=environ['GOOGLE_API_RESTIES']
		)
	# use requests to lookup place
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
		newPlace = GooglePlace(result['place_id'],result) #GooglePlace neeeds id and result
		#filter out anywhere permanently closed
		#maybe keep and notify instead?
		if not newPlace.permanently_closed:
			places.append(newPlace)

	return places

def addPlaceToDB(placeID, placeName):
	''' insert a place into the database'''
	# just print for now
	print('{} has ID: {}'.format(placeID, placeName))
	return None

##############
### routes ###
##############

@places_blueprint.route('/')
def places():
	return render_template(
		'places.html',
		places=getPlaces()
	)

@login_required
@places_blueprint.route('/search', methods=['GET','POST'])
def search():
	form = SearchForm()
	if request.method == 'POST':
		searchTerm = form.searchTerm.data
		return redirect(url_for('places.results', searchTerm=searchTerm))
	return render_template('search.html',form=form)


@login_required
@places_blueprint.route('/results/<string:searchTerm>',  methods=['GET','POST'])
def results(searchTerm):

	#TODO: finish front end search form
	#	--attributes
	#search form on home screen or in header!

	#if post, add selected to db
	
	if request.method == 'POST':
		addPlaceToDB(placeID, placeName)
		return redirect(url_for('places.details',placeID='ChIJ02oH5Oe3t4kRBgaBDTK91VQ'))


	return render_template(
		'results.html',
		places = searchForPlace(searchTerm),
		form = SearchForm(),
		searchTerm = searchTerm
	)

#how to get two params?
@places_blueprint.route('/addPlace/<placeID>', methods=['POST'])
@login_required
def addPlace(placeID1):
	addPlaceToDB(placeID)
	return redirect(url_for('places.places'))


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