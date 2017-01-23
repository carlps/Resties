# project/users/views.py

###############
### imports ###
###############

from functools import wraps
from flask import flash, redirect, render_template, request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError

from .forms import RegisterForm, LoginForm
from project import db, bcrypt
from project.models import User

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
	def wrap(*arg, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('users.login'))
	return wrap

##############
### routes ###
##############

@users_blueprint.route('/logout/')
@login_required
def logout():
	'''remove logged in and user credentials
	from session. redirect to login page'''
	session.pop('logged_in', None)
	session.pop('user_id', None)
	session.pop('role', None)
	flash('Goodbye!')
	return redirect(url_for('users.login'))

@users_blueprint.route('/login', methods=['GET','POST'])
def login():

	# For some reason, when click submit, the request.method post does nothing.

	error = None
	form = LoginForm(request.form)
	print('ayyyy')
	if request.method == 'POST':
		print('lmao')
		if form.validate_on_submit():
			user = User.query.filter_by(userName=request.form['name']).first()
			if user is not None and bcrypt.check_password_hash(
					user.password,request.form['password']):
				session['logged_in'] = True
				session['user_id'] = user.id
				session['role'] = user.role
				flash('Welcome {}!'.format(user.name))
				redirect(url_for('places.places'))
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
				form.name.data,
				form.email.data,
				bcrypt.generate_password_hash(form.password.data)
			)
			try:
				db.session.add(new_user)
				db.session.commit()
				flash('Thanks for registering. Please login.')
				return redirect(url_for('users.login'))
			except IntegrityError:
				error = 'That username and/or email already exist.'
				return render_template('register.html', form=form, error=error)
	return render_template('register.html', form=form, error=error)