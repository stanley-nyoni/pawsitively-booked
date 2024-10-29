import unittest
from app import app, db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        user = User(username='jane_doe', email='jane@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        retrieved_user = User.query.filter_by(username='jane_doe').first()
        self.assertIsNotNone(retrieved_user)

    def test_check_password(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('mysecret')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.check_password('mysecret'))
        self.assertFalse(user.check_password('wrongpass'))

    def test_update_user(self):
        user = User(username='john_doe', email='john@example.com')
        db.session.add(user)
        db.session.commit()
        user.email = 'john_updated@example.com'
        db.session.commit()
        updated_user = User.query.filter_by(username='john_doe').first()
        self.assertEqual(updated_user.email, 'john_updated@example.com')

    def test_delete_user(self):
        user = User(username='delete_me', email='delete@example.com')
        db.session.add(user)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        self.assertIsNone(User.query.filter_by(username='delete_me').first())

if __name__ == '__main__':
    unittest.main()
