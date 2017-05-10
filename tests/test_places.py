# tests/test_users.py


import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import Place

TEST_DB = 'test.db'


class PlacesTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()


    ########################
    #### helper methods ####
    ########################
    
    def login(self, userName='isaac', password='iceyboi'):
        return self.app.post(
            '/login',
            data=dict(userName=userName, password=password), 
            follow_redirects=True)

    def register(self, userName='isaac', email='iceman@yoohoo.com', password='iceyboi', confirm='iceyboi', zipCode='87004'):
        return self.app.post(
            '/register/',
            data=dict(userName=userName, email=email,
                        password=password, confirm=confirm,
                        zipCode=zipCode),
            follow_redirects=True
            )
    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def createUser(self, userName, email, password, zipCode):
        newUser = User(userName=userName,
                        email=email,
                        password=bcrypt.generate_password_hash(password),
                        zipCode=zipCode
                        )
        db.session.add(newUser)
        db.session.commit()


    #############
    ### tests ###
    #############

    def test_logged_in_users_access_places_list(self):
    	self.register()
    	response = self.login()
    	self.assertIn(b"Either you don\'t have any resties or something weird is going on.",response.data)

    def test_not_logged_in_users_cannot_access_places_list(self):
    	response = self.app.get('/', follow_redirects=True)
    	self.assertIn(b'Might I suggest <a href="/login">logging in</a> or <a href="/register"> signing up',response.data)

    def test_users_can_add_places(self):
    	self.register()
    	self.login()
    	response = self.app.post('/addPlace/ChIJ-6zk5ZO3t4kRwi3BXpaCRjE', follow_redirects=True)
    	self.assertIn(b'Momofuku CCDC is added to your list!', response.data)

    def test_users_cannot_add_invalid_places(self):
    	self.register()
    	self.login()
    	response = self.app.get('/addPlace/abc123', follow_redirects=True)
    	self.assertEqual(response.status_code,405)
    	self.assertIn(b"Method not allowed. Were you trying to do something you\'re not supposed to???", response.data)

if __name__ == '__main__':
    unittest.main()