# project/users/views.py

###############
### imports ###
###############

from functools import wraps
from flask import flash, redirect, render_template, request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError

from .forms import RegisterForm, LoginForm
from project import db, bcrypt
from project.models import User, ZipCode
import requests
from os import environ

##############
### config ###
##############

users_blueprint = Blueprint('users', __name__)

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

def geolocateZip(zipCode):
	'''use google maps API to geocode a zip
	   AKA takes a zip and returns tuple of zip,lat,long'''

	# create url for looking up zip
	url = ('https://maps.googleapis.com/maps/api/geocode/'
		   'json?address={}&key={}'.format(zipCode,environ['GOOGLE_API_RESTIES']))
	# use requests to request data 
	request = requests.get(url)
	# ensure valid response 
	if request.status_code != 200:
		raise AttributeError('Request returned bad response')
	else:
		# if valid response, return results from json response
		results = request.json()['results']
	# if more than one result, raise error (need to test)
	if len(results) > 1:
		raise AttributeError('Zip search returned more than one result?')

	# if only one respone, pull lat and long out of json
	# response has other info, but this is all we need (for now?)
	lat, lng = results[0]['geometry']['location'].values()
	# return tuple with zip, latitude, longitude
	return (zipCode,lat,lng)

def checkZip(zipCode):
	'''query db for zip code
	   if already in zipCode table, do nothing
	   if not, geolocate and insert'''

	# query db for passed zip
	lookup = ZipCode.query.filter_by(zipCode=zipCode).first()
	# if nothing returned
	if lookup is None:
		# geolocateZip returns (zip, lat, lng)
		geo = geolocateZip(zipCode)
		# create new ZipCode object
		new_zip = ZipCode(*geo)
		#add new zip code to db
		db.session.add(new_zip)
		db.session.commit()


##############
### routes ###
##############

@users_blueprint.route('/logout/')
@login_required
def logout():
	'''remove logged in and user credentials
	from session. redirect to login page'''
	session.pop('logged_in', None)
	session.pop('userID', None)
	session.pop('role', None)
	flash('Goodbye!')
	return redirect(url_for('places.places'))

@users_blueprint.route('/login', methods=['GET','POST'])
def login():
	error = None
	form = LoginForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(userName=request.form['name']).first()
			if user is not None and bcrypt.check_password_hash(
					user.password, request.form['password']):
				session['logged_in'] = True
				session['userID'] = user.userID
				session['role'] = user.role
				flash('Welcome {}!'.format(user.userName)) #can I make flash a toast?
				return redirect(url_for('places.places'))
			else:
				error = 'Invalid username or password'
		else:
			error = 'invalid yo'
	return render_template('login.html', form=form, error=error)

@users_blueprint.route('/register/', methods=['GET','POST'])
def register():
	error = None
	form = RegisterForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			new_user = User(
				userName=form.name.data,
				email=form.email.data,
				password=bcrypt.generate_password_hash(form.password.data),
				zipCode=form.zipCode.data
			)
			checkZip(form.zipCode.data)
			try:
				db.session.add(new_user)
				db.session.commit()
				flash('Thanks for registering. Please login.')
				return redirect(url_for('users.login'))
			except IntegrityError:
				error = 'That username and/or email already exist.'
				return render_template('register.html', form=form, error=error)
	return render_template('register.html', form=form, error=error)