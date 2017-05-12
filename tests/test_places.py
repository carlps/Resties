# tests/test_users.py


import os
import unittest
from datetime import date

from project import app, db, bcrypt
from project._config import basedir
from project.models import Place, User

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

    def test_users_can_access_place_details(self):
    	self.register()
    	self.login()
    	self.app.post('/addPlace/ChIJ-6zk5ZO3t4kRwi3BXpaCRjE', follow_redirects=True)
    	response = self.app.get('/details/ChIJ-6zk5ZO3t4kRwi3BXpaCRjE', follow_redirects=True)
    	self.assertIn(b'Momofuku CCDC', response.data)

    '''#can't do it because date...
    def test_users_can_add_visits(self):
    	self.register()
    	self.login()
    	self.app.post('/addPlace/ChIJ-6zk5ZO3t4kRwi3BXpaCRjE', follow_redirects=True)
    	response= self.app.post('/addVisit/ChIJ-6zk5ZO3t4kRwi3BXpaCRjE', 
    		data=dict(visitDate='01-01-2017', 
    				  comments='visited new years.',
    				  userID=1,
    				  placeID='ChIJ-6zk5ZO3t4kRwi3BXpaCRjE'
    				 ),
    		follow_redirects=True)
    	self.assertIn(b'Visit recorded! I hope you enjoyed!', response.data)
	'''
    #users_can_edit_visits

    def test_users_can_edit_notes(self):
    	self.register()
    	self.login()
    	self.app.post('/addPlace/ChIJ-6zk5ZO3t4kRwi3BXpaCRjE', follow_redirects=True)
    	response = self.app.post('/editNotes/ChIJ-6zk5ZO3t4kRwi3BXpaCRjE',
    							data = dict(notes='Cool spot.'),
    							follow_redirects=True
    			)
    	self.assertIn(b'Cool spot.', response.data)

    def test_users_can_search_for_places(self):
    	self.register()
    	self.login()
    	response = self.app.post('/search',
    					data=dict(searchTerm='the range'), 
    					follow_redirects=True)
    	self.assertIn(b'/addPlace/ChIJ95RxxRN4IocRUhvj7gXGxEo',response.data)

    def test_no_add_place_link_if_already_in_list(self):
    	self.register()
    	self.login()
    	self.app.post('/addPlace/ChIJ95RxxRN4IocRUhvj7gXGxEo', follow_redirects=True)
    	response = self.app.post('/search',
    					data=dict(searchTerm='the range'), 
    					follow_redirects=True)
    	self.assertNotIn(b'/addPlace/ChIJ95RxxRN4IocRUhvj7gXGxEo',response.data)

    def test_added_place_in_list_on_home_page(self):
    	self.register()
    	self.login()
    	self.app.post('/addPlace/ChIJ95RxxRN4IocRUhvj7gXGxEo', follow_redirects=True)
    	response = self.app.get('/', follow_redirects=True)
    	self.assertIn(b'The Range Cafe', response.data)

    # maybe test GooglePlace attributes?


if __name__ == '__main__':
    unittest.main()