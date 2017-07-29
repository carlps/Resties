# project/_config.py


import os
from binascii import hexlify

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE= 'resties.db'
CSRF_ENABLED = True
SECRET_KEY = hexlify(os.urandom(24))
DEBUG = True

# define full path for database 
DATABASE_PATH = os.path.join(basedir,DATABASE)

# database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH