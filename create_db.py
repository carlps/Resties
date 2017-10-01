""" Create all models in postges db
"""

from os import environ

from sqlalchemy import create_engine

from project import db
from project.models import Place, User, UserPlace, Visit, ZipCode

db.create_all()
db.session.commit()
