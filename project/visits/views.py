# visits/views.py

###############
### imports ###
###############

from functools import wraps
from flask import (flash, redirect, render_template, 
				  request, session, url_for, Blueprint, abort)

from project import db
from project.models import Visits

##############
### config ###
##############

visits_blueprint = Blueprint('visits', __name__)

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

