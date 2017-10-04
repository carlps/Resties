# tests/test_users.py


import os
import unittest

from project import app, db, bcrypt
from project._config import basedir
from project.models import User, ZipCode

os.environ['APP_SETTINGS'] = "project._config.TestingConfig"


class UsersTests(unittest.TestCase):

    ############################
    #    setup and teardown    #
    ############################

    # executed prior to each test
    def setUp(self):
        app.config.from_object(os.environ['APP_SETTINGS'])
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    # executed after each test
    def tearDown(self):
        for user in User.query.all():
            print(user.userID, user.userName)
        db.session.remove()
        db.drop_all()

    ########################
    #    helper methods    #
    ########################

    def login(self, userName='isaac', password='iceyboi', valid=True):
        ''' Helper method to login user. Defaults to defaults
        throughout this file. 'valid' parameter is whether the login
        should be expected to be valid or not. '''
        response = self.app.post(
            '/login',
            data=dict(userName=userName, password=password),
            follow_redirects=True)
        if valid:
            self.assertIn('Welcome, {}'.format(userName), str(response.data))
        else:
            self.assertNotIn('Welcome, {}'.format(userName),
                             str(response.data))
        return response

    def register(self, userName='isaac', email='iceman@yoohoo.com',
                 password='iceyboi', confirm='iceyboi',
                 zipCode='87004', valid=True):
        ''' Registers a user to the app. Defaults to default dummy data.
        "valid" is whether or not the registration data is valid '''
        print(userName, email)
        response = self.app.post(
            '/register/',
            data=dict(userName=userName, email=email,
                      password=password, confirm=confirm,
                      zipCode=zipCode),
            follow_redirects=True
        )
        if valid:
            self.assertIn(b'Thanks for registering. Please login.',
                          response.data)
        else:
            self.assertNotIn(b'Thanks for registering. Please login.',
                             response.data)
        return response

    def logout(self, valid=True):
        response = self.app.get('logout/', follow_redirects=True)
        if valid:
            self.assertIn(b'Goodbye!', response.data)
        else:
            self.assertNotIn(b'Goodbye!', response.data)
        return response

    def createUser(self, userName, email, password, zipCode):
        newUser = User(userName=userName,
                       email=email,
                       password=bcrypt.generate_password_hash(password),
                       zipCode=zipCode
                       )
        db.session.add(newUser)
        db.session.commit()

    #############
    #   tests   #
    #############

    def test_users_can_register(self):
        response = self.register('isaac', 'iceman@gmail.com', 'iceyboi',
                                 'iceyboi', '87004', True)
        self.assertIn(b'Thanks for registering. Please login.', response.data)

    def test_login_link_is_present_on_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/login"', response.data)

    def test_users_cant_login_unless_registered(self):
        response = self.login('nobody', 'nopass', False)
        self.assertIn(b'Invalid username or password', response.data)

    def test_users_can_login(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004', True)
        response = self.login('isaac', 'iceyboi')
        self.assertIn(b'Welcome, isaac!', response.data)

    def test_login_invalid_form_data(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004', True)
        response = self.login("' OR 1=1; --", 'password123', False)
        self.assertIn(b'Invalid username or password', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Please register to begin listing restaurants.', response.data)

    def test_user_registration_error_duplicate(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004', True)
        response = self.register('isaac', 'iceman@yoohoo.com',
                                 'iceyboi', 'iceyboi', '87004', False)
        self.assertIn(
            b'That username and/or email already exist.', response.data)

    def test_user_registration_error_pword(self):
        response = self.register('isaac', 'iceman@yoohoo.com',
                                 'iceyboi', 'iceyboi2', '87004', False)
        self.assertIn(b"Passwords didn&#39;t match", response.data)

    def test_user_registration_invalid_zip_alpha(self):
        response = self.register('isaac', 'iceman@yoohoo.com', 'iceyboi',
                                 'iceyboi', '87OO4', False)
        self.assertIn(b'Zip code can only be numeric values', response.data)

    def test_user_registration_invalid_zip_length(self):
        response = self.register('isaac', 'iceman@yoohoo.com',
                                 'iceyboi', 'iceyboi', '123456789', False)
        self.assertIn(b'Zip Code must be exactly 5 digits', response.data)

    def test_logged_in_users_can_logout(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004', True)
        self.login('isaac', 'iceyboi')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout(valid=False)
        self.assertNotIn(b'Goodbye!', response.data)

    def test_default_user_role(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004', True)

        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.role, 'user')

    def test_new_zip(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004')
        zip = ZipCode.query.filter_by(zipCode='87004').first()
        self.assertEqual(zip.zipCode, '87004')

    def test_new_zip_latitude(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004')
        zip = ZipCode.query.filter_by(zipCode='87004').first()
        self.assertEqual(zip.latitude, 35.3180691)

    def test_new_zip_longitude(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004')
        zip = ZipCode.query.filter_by(zipCode='87004').first()
        self.assertEqual(zip.longitude, -106.5466221)

    def test_duplicate_zip(self):
        self.register('isaac', 'iceman@yoohoo.com',
                      'iceyboi', 'iceyboi', '87004')
        self.register('mario', 'moxpod@yeehee.cem',
                      'moxyboi', 'moxyboi', '87004')
        zip = ZipCode.query.all()
        self.assertEqual(1, len(zip))

if __name__ == '__main__':
    unittest.main()
