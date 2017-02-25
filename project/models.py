# project/models.py

from project import db
import requests
from os import environ

class Place(db.Model):

	__tablename__ = 'places'

	placeID = db.Column(db.String, primary_key=True)
	placeName = db.Column(db.String, nullable=False)
	notes = db.Column(db.String, nullable=True)
	userID = db.Column(db.Integer, db.ForeignKey('users.userID'), primary_key=True)

	def __init__(self, placeID, placeName, notes, userID):
		self.placeID = placeID
		self.placeName = placeName
		self.notes = notes
		self.userID = userID

	def __repr__(self):
		return '<name {0}>'.format(self.placeName)

class User(db.Model):
	
	__tablename__ = 'users'

	userID = db.Column(db.Integer, primary_key=True)
	userName = db.Column(db.String, unique=True, nullable=False)
	email = db.Column(db.String, unique=True, nullable=False)
	password = db.Column(db.String, nullable=False)
	role = db.Column(db.String, default='user')
	zipCode = db.Column(db.String, nullable=False)
	places = db.relationship('Place',backref='saver')

	def __init__(self, userName, email, password, role, zipCode):
		self.userName = userName
		self.email = email
		self.password = password
		self.role = role
		self.zipCode = zipCode


	def __repr__(self):
		return '<User {)}>'.format(self.userName)

class Visit(db.Model):

	__tablename__ = 'visits'

	visitID = db.Column(db.Integer, primary_key=True)
	visitDate = db.Column(db.Date, nullable=False)
	comments = db.Column(db.String, nullable=True)
	userID = db.Column(db.Integer, db.ForeignKey('users.userID'))
	placeID = db.Column(db.String, db.ForeignKey('places.placeID'))

	def __init__(self, visitDate, comments, userID, placeID):
		self.visitDate = visitDate
		self.comments = comments
		self.userID = userID
		self.placeID = placeID

class GooglePlace(object):
	"""A place (usually restaurant or bar) as pulled from 
	Google Places API. 

	Not meant to be stored in DB. Used when detail data is
	pulled from google API in app.

	GooglePlace has the following properties:

	Attributes:
		address_components: A list of dicts containing seperate 
							adress components
			types: type(s) of components. ex: ["country","political"]
			long_name: the full text description of the address component. 
					   ex: "United States"
			short_name: the abbreviation (if available). ex: "US" 
						if no short name, short_name will be == long_name
		formatted_address: A string of the human readable address. 
						   ex: '1513 17th St NW, Washington, DC 20036, USA'
		formatted_phone_number: A string of the phone number in local format.
								ex: "(202) 733-5623"
		adr_address: A string of the address in adr microformat
		geometry: A dict containing two dicts with geo info:
			location: a dict with two floats 'lat' and 'lng' containing 
					  latitude and longitude
			viewport: a dict containing preferred viewport for a map with 
					  this place
					  keys are 'notheast' and 'southest' both containing 
					  dicts identical in format to location
		icon: A string with the URL to a suggested map icon
		international_phone_number: A string with the phone number in 
									international format
						   			ex: '+1 202-733-5623'
		name: A string with the human-readable name (AKA the business name)
			  ex: "Duke's Grocery"
		opening_hours: A dict with info on the hours of operation for 
					   the place
			open_now: A bool of whether or not the plaaceis open at 
					  current time
			peiods: A list of 7 days. each contains a dict with the following:
				open: a dict of when the place opens:
					day: an int from 0-6 corresponding to day of the week. 
						 0 = Sun, 6 = Sat.
					time: a string with time of day in 24 hour hhmm format 
						 (in the place's timezone)
					  	 if a place is always open, day will be 0 and time 
					  	 will be '0000'.
				close: same as open, but for when it closes. if it closes 
					   after midnight, the day will be +1. If a place is 
					   always open, there will be no close section.   
			weekday_text: A list of seven strings with formatted open hours
						  ex: [0] == 'Monday: 11:00 AM - 2:00 AM'
		permanently_closed: A bool if the place is permanently closed. 
							Not in response if false
		photos: A list of dicts which contain references to images:
			photo_reference: a string with a unique ID for a photo request
			height: an int of max height of the image
			widhth: an int of max width of the image
			html_attributions: a list of attibutions. always present but 
							   may be empty 
		place_id: A string with the unique ID. Used to get info about 
				  the place.
				  ex: 'ChIJ5_UoOcG3t4kRuuU-rbm7vtc' 
		scope: A string with the scope of the place_id. 
			   either 'APP' or 'GOOGLE' 
			   if "APP", the ID is unique to your app. 
			   if "GOOGLE", it is public
		alt_ids: only used if local id
		price_level: An int from 0 to 4 of the level of price 
					 decided by google.
					 0 == free, 4 == very expensive
		rating: A float of google's aggregated rating
		types: A list of feature types (all strings) describing the place. 
			   usually 'restaurant', 'food', 'bar', etc
		url: A string with the url to the google page for the place. 
			 Applications must link to or embed this page on any screen 
			 that shows detailed results about the place to the user.
		utc_offset: An int with the number of minutes this place's 
					timezone is from UTC
					EST is -300 which is 5 hrs
		vicinity: A string with the simplified address for the place. 
				  Just street address + locality. Nothing higher.
				  ex: '1513 17th Street Northwest, Washington'
		website:A string with the business' website

	Probably not all properties will be used, but would rather have and not 
	need than need and not have. One property (reviews) is left out as it's 
	large and not wanted.

	See more details about places and attributes at:
	https://developers.google.com/places/web-service/details#PlaceDetailsResults
	"""
	def __init__(self, placeID):
		''' I think take placeID as param, then lookup and set all other 
		attributes with placeID in this __init__
		use checkAttr to make sure attribute is in response

		'''
		self.placeID = placeID
		#call function to get json object with place data
		self.lookup = self.lookupPlace(placeID)['result']

		#set attributes
		self.address_components = self.checkAttr(self.lookup,'address_components')
		self.adr_address = self.checkAttr(self.lookup,'adr_address')
		self.formatted_address = self.checkAttr(self.lookup,'formatted_address')
		self.formatted_phone_number = self.checkAttr(self.lookup,'formatted_phone_number')
		self.geometry = self.checkAttr(self.lookup,'geometry')
		self.icon = self.checkAttr(self.lookup,'icon')
		self.international_phone_number = self.checkAttr(self.lookup,'international_phone_number')
		self.name = self.checkAttr(self.lookup,'name')
		self.opening_hours = self.checkAttr(self.lookup,'opening_hours')
		self.photos = self.checkAttr(self.lookup,'photos')
		self.permanently_closed = self.checkAttr(self.lookup,'permanently_closed')
		self.place_id = self.checkAttr(self.lookup,'place_id')
		self.price_level = self.checkAttr(self.lookup,'price_level')
		self.rating = self.checkAttr(self.lookup,'rating')
		self.scope = self.checkAttr(self.lookup,'scope')
		self.types = self.checkAttr(self.lookup,'types')
		self.url = self.checkAttr(self.lookup,'url')
		self.utc_offset = self.checkAttr(self.lookup,'utc_offset')
		self.vicinity = self.checkAttr(self.lookup,'vicinity')
		self.website = self.checkAttr(self.lookup,'website')

	def lookupPlace(self,placeID):
		'''lookup place based on placeID and return json response'''

		url = ('https://maps.googleapis.com/maps/api/place'
			  '/details/json?placeid={}&key={}').format(
			  	placeID,environ['GOOGLE_API_RESTIES'])
			  
		request = requests.get(url)
		if request.status_code != 200:
			raise AttributeError('Request returned bad response')
		else:
			return request.json()

	def checkAttr(self,lookup,attr):
		'''because not all places return an attribute
		use this to check if an attribute is returned or not
		if not, set to None
		'''
		if attr in lookup:
			return lookup[attr]
		else:
			return None

	def __str__(self):
		return self.name