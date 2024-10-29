'''Test the home page'''

from app import app, db
import unittest

class BasicTestCase(unittest.TestCase):
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

    def test_home_page(self):
        '''Test the home page'''
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_page(self):
        '''Test the index page'''
        response = self.app.get('/index')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        '''Test the login page'''
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        '''Test the register page'''
        response = self.app.get('/signup')
        self.assertEqual(response.status_code, 200)
    
    def test_features_page(self):
        '''Test the feature page'''
        response = self.app.get('/features')
        self.assertEqual(response.status_code, 200)

    def test_faq_page(self):
        '''Test the FAQ page'''
        response = self.app.get('/faqs')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page(self):
        '''Test the dashboard page'''
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 302)



if __name__ == '__main__':
    unittest.main()
