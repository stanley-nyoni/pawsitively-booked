'''Tests for the routes module.'''

import unittest
from app import app, db

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        '''Set up the test client'''
        app.config.from_object('config.TestConfig')
        self.app = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        '''Tear down the test client'''
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Dog registration routes
    def test_dog_registration_status_code(self):
        '''Check the status code for dog registration page.'''
        response = self.app.get('/dog_registration')
        self.assertEqual(response.status_code, 302)

    def test_facility_registration_status_code(self):
        '''Check the status code for facility registration page.'''
        response = self.app.get('/facility_registration')
        self.assertEqual(response.status_code, 302)

    # Dashboard routes
    def test_dog_owner_dashboard_access(self):
        '''Check access to dog owner dashboard.'''
        response = self.app.get('/dashboard/dog_owner')
        self.assertEqual(response.status_code, 302)

    def test_facility_owner_dashboard_access(self):
        '''Check access to facility owner dashboard.'''
        response = self.app.get('/dashboard/facility_owner')
        self.assertEqual(response.status_code, 302)

    # Login routes
    def test_login_dog_owner_status_code(self):
        '''Check login page status for dog owners.'''
        response = self.app.get('/login/dog_owner')
        self.assertEqual(response.status_code, 200)

    def test_login_facility_owner_status_code(self):
        '''Check login page status for facility owners.'''
        response = self.app.get('/login/facility_owner')
        self.assertEqual(response.status_code, 200)

    # Signup routes
    def test_signup_dog_owner(self):
        '''Check signup page for dog owners.'''
        response = self.app.get('/signup/dog_owner')
        self.assertEqual(response.status_code, 200)

    def test_signup_facility_owner(self):
        '''Check signup page for facility owners.'''
        response = self.app.get('/signup/facility_owner')
        self.assertEqual(response.status_code, 200)

    # Logout route
    def test_logout_redirect(self):
        '''Check logout functionality redirects.'''
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 302)

    # Dog owner-specific routes
    def test_create_booking_access(self):
        '''Check access to the create booking page for dog owners.'''
        response = self.app.get('/dog_owner/create_booking')
        self.assertEqual(response.status_code, 302)

    def test_dog_profile_access(self):
        '''Check access to dog profile page for dog owners.'''
        response = self.app.get('/dog_owner/dog_profile')
        self.assertEqual(response.status_code, 302)

    def test_user_profile_access(self):
        '''Check access to user profile page for dog owners.'''
        response = self.app.get('/dog_owner/user_profile')
        self.assertEqual(response.status_code, 302)

    # Facility owner-specific routes
    def test_facility_owner_profile_access(self):
        '''Check access to user profile page for facility owners.'''
        response = self.app.get('/facility_owner/user_profile')
        self.assertEqual(response.status_code, 302)

    # Other routes
    def test_set_location_access(self):
        '''Check access to set location page.'''
        response = self.app.get('/set_location')
        self.assertEqual(response.status_code, 302)

    def test_account_settings_access(self):
        '''Check access to account settings page.'''
        response = self.app.get('/account/settings')
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
