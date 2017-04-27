# project/test_users.py


import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class UsersTests(unittest.TestCase):

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
    
    def login(self, userName, password):
        return self.app.post(
            '/login',
            data=dict(userName=userName, password=password), 
            follow_redirects=True)

    def register(self, userName, email, password, confirm, zipCode):
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
    
    def test_users_can_register(self):
        response = self.register('isaac', 'iceman@gmail.com', 'iceyboi', 'iceyboi','87004')
        self.assertIn(b'Thanks for registering. Please login.', response.data)

    def test_login_link_is_present_on_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/login"',response.data)

    def test_users_cant_login_unless_registered(self):
        response = self.login('nobody','nopass')
        self.assertIn(b'Invalid username or password',response.data)

    def test_users_can_login(self):
        self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','87004')
        response = self.login('isaac','iceyboi')
        self.assertIn(b'Welcome isaac!', response.data)

    def test_login_invalid_form_data(self):
        self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','87004')
        response = self.login("' OR 1=1; --",'password123')
        self.assertIn(b'Invalid username or password', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code,200)
        self.assertIn(b'Please register to begin listing restaurants.',response.data)

    def test_user_registration_error_duplicate(self):
        self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','87004')
        response = self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','87004')
        self.assertIn(b'That username and/or email already exist.',response.data)

    def test_user_registration_error_pword(self):
        response = self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi2','87004')
        self.assertIn(b"Passwords didn&#39;t match", response.data)

    def test_user_registration_invalid_zip_alpha(self):
        response = self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','87OO4')
        self.assertIn(b'Zip code can only be numeric values', response.data)

    def test_user_registration_invalid_zip_length(self):
        response = self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','123456789')
        self.assertIn(b'Zip Code must be exactly 5 digits', response.data)

    def test_logged_in_users_can_logout(self):
        # THIS ONE IS FAILING AND IDK WHY
        self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','87004')
        # LOGIN ISN'T LOGGING IN
        self.login('issac','iceyboi')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye!',response.data)

    def test_default_user_role(self):
        self.register('isaac','iceman@yoohoo.com', 'iceyboi', 'iceyboi','87004')

        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.role,'user')

    #geolocate zip
    #check zip

if __name__ == '__main__':
    unittest.main()