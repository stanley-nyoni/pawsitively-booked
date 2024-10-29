import unittest
from app import app, db
from app.models import User, Facility, Review

class ReviewModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(username='reviewer', email='reviewer@example.com')
        self.facility = Facility(name='Pet Palace')
        db.session.add(self.user)
        db.session.add(self.facility)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_review(self):
        review = Review(rating=5.0, comment='Excellent!', user_id=self.user.id, facility_id=self.facility.id)
        db.session.add(review)
        db.session.commit()
        retrieved_review = Review.query.first()
        self.assertIsNotNone(retrieved_review)

    def test_update_review(self):
        review = Review(rating=4.0, comment='Good service.', user_id=self.user.id, facility_id=self.facility.id)
        db.session.add(review)
        db.session.commit()
        review.comment = 'Very good service.'
        db.session.commit()
        updated_review = Review.query.first()
        self.assertEqual(updated_review.comment, 'Very good service.')

    def test_delete_review(self):
        review = Review(rating=3.0, user_id=self.user.id, facility_id=self.facility.id)
        db.session.add(review)
        db.session.commit()
        db.session.delete(review)
        db.session.commit()
        self.assertIsNone(Review.query.first())

if __name__ == '__main__':
    unittest.main()
