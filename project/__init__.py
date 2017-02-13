from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_pyfile('_config.py')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.jinja_env.add_extension('jinja2.ext.do')

from project.users.views import users_blueprint
from project.places.views import places_blueprint

# register our blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(places_blueprint)