# db_create.py

from project import db
from project.models import Place, User, Visit, ZipCode

db.create_all()


#insert some test data
'''
db.session.add(
    User("admin", "ad@min.com", "admin", "admin")
)

db.session.add(
	Place('ChIJ-6zk5ZO3t4kRwi3BXpaCRjE', 'Momofuku CCDC','buns n tings', 1)
)
'''
db.session.commit()