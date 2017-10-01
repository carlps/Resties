import os
import datetime

from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.jinja_env.add_extension('jinja2.ext.do')

from project.users.views import users_blueprint
from project.places.views import places_blueprint

print(os.environ['APP_SETTINGS'])

# register our blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(places_blueprint)

@app.errorhandler(404)
def not_found(error):
	if app.debug is not True:
		now = datetime.datetime.now()
		r = request.url
		with open('error.log', 'a') as f:
			current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
			f.write("\n404 error at {}: {} ".format(current_timestamp, r))
	return render_template('404.html'), 404

@app.errorhandler(405)
def not_found(error):
	if app.debug is not True:
		now = datetime.datetime.now()
		r = request.url
		with open('error.log', 'a') as f:
			current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
			f.write("\n405 error at {}: {} ".format(current_timestamp, r))
	return render_template('405.html'), 405

@app.errorhandler(500)
def internal_error(error):
	if app.debug is not True:
		now = datetime.datetime.now()
		r = request.url
		with open('error.log', 'a') as f:
			current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
			f.write("\n500 error at {}: {} ".format(current_timestamp, r))
	return render_template('500.html'), 500
