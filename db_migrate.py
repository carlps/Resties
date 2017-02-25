# db_migrate.py

import sqlite3
from project import db, bcrypt

from project._config import DATABASE_PATH


# fix admin password
with sqlite3.connect(DATABASE_PATH) as connection:

	# get a cursor object to execute SQL commands
	c = connection.cursor()
	

	# get admin record password
	c.execute("""SELECT password
				 FROM users
				 WHERE userID = 1""")

	# hash password with bcrypt
	encrypted = bcrypt.generate_password_hash(c.fetchone()[0])

	# update record
	c.execute("""UPDATE users
				 SET password = (?)
				 WHERE userID = 1""",(encrypted,))
