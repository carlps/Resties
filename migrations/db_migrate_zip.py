# db_migrate.py

import sqlite3
from project import db

from project._config import DATABASE_PATH

with sqlite3.connect(DATABASE_PATH) as connection:

	# get a cursor object to execute SQL commands
	c = connection.cursor()
	
	# temporarily change the name of users table
	c.execute("""ALTER TABLE users RENAME TO old_users""")

	# recreate a new users table with updated schema
	db.create_all()

	# retrieve data from old_users table
	# default zip code to 20009
	c.execute("""SELECT userName, email, password, role
				 FROM old_users
				 ORDER BY userID ASC""")

	# save all rows as a list of tupsles; set zipCode to 20009
	data = [(row[0], row[1], row[2], row[3], 20009) for row in c.fetchall()]

	# insert data into users table
	c.executemany("""INSERT INTO users (userName, email, password,
					 role, zipCode) VALUES(?,?,?,?,?)""", data)

	# delete old_users table
	c.execute("DROP TABLE old_users")