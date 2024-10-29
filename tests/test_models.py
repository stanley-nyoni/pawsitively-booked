import unittest
from app import app, db
from datetime import datetime, timedelta
from app.models import User, Dog, Facility, DogOwner, FacilityOwner, Booking, Review

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client and database."""
        app.config.from_object('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Tear down the test client and database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ---------- User Model Tests ----------
    def test_create_user(self):
        """Test creating a user."""
        user = User(first_name='John', last_name='Doe', username='johndoe', email='johndoe@gmail.com')
        db.session.add(user)
        db.session.commit()

        self.assertEqual(User.query.count(), 1)

    def test_user_attributes(self):
        """Test the user attributes."""
        user = User(first_name='John', last_name='Doe', username='johndoe', email='johndoe@gmail.com')
        db.session.add(user)
        db.session.commit()

        saved_user = User.query.first()
        self.assertEqual(saved_user.first_name, 'John')
        self.assertEqual(saved_user.last_name, 'Doe')
        self.assertEqual(saved_user.username, 'johndoe')
        self.assertEqual(saved_user.email, 'johndoe@gmail.com')

    # ---------- Dog Model Tests ----------
    def test_create_dog(self):
        """Test creating a dog."""
        dog = Dog(name='Rover', breed='German Shepherd', age=2)
        db.session.add(dog)
        db.session.commit()

        self.assertEqual(Dog.query.count(), 1)

    def test_dog_attributes(self):
        """Test the dog attributes."""
        dog = Dog(name='Rover', breed='German Shepherd', age=2)
        db.session.add(dog)
        db.session.commit()

        saved_dog = Dog.query.first()
        self.assertEqual(saved_dog.name, 'Rover')
        self.assertEqual(saved_dog.breed, 'German Shepherd')
        self.assertEqual(saved_dog.age, 2)

    # ---------- Facility Model Tests ----------
    def test_create_facility(self):
        """Test creating a facility."""
        facility = Facility(name='Dog Park', location='Lekki', capacity=100)
        db.session.add(facility)
        db.session.commit()

        self.assertEqual(Facility.query.count(), 1)

    def test_facility_attributes(self):
        """Test the facility attributes."""
        facility = Facility(name='Dog Park', location='Lekki', capacity=100)
        db.session.add(facility)
        db.session.commit()

        saved_facility = Facility.query.first()
        self.assertEqual(saved_facility.name, 'Dog Park')
        self.assertEqual(saved_facility.location, 'Lekki')
        self.assertEqual(saved_facility.capacity, 100)

    # ---------- DogOwner Model Tests ----------
    def test_create_dog_owner(self):
        """Test creating a dog owner."""
        dog_owner = DogOwner(first_name='John', last_name='Doe', username='johndoe', email='johndoe@gmail.com')
        db.session.add(dog_owner)
        db.session.commit()

        self.assertEqual(DogOwner.query.count(), 1)

    def test_dog_owner_attributes(self):
        """Test the dog owner attributes."""
        dog_owner = DogOwner(first_name='John', last_name='Doe', username='johndoe', email='johndoe@gmail.com')
        db.session.add(dog_owner)
        db.session.commit()

        saved_owner = DogOwner.query.first()
        self.assertEqual(saved_owner.first_name, 'John')
        self.assertEqual(saved_owner.last_name, 'Doe')
        self.assertEqual(saved_owner.username, 'johndoe')
        self.assertEqual(saved_owner.email, 'johndoe@gmail.com')

    # ---------- FacilityOwner Model Tests ----------
    def test_create_facility_owner(self):
        """Test creating a facility owner."""
        facility_owner = FacilityOwner(first_name='Jane', last_name='Doe', username='janedoe', email='janedoe@gmail.com')
        db.session.add(facility_owner)
        db.session.commit()

        self.assertEqual(FacilityOwner.query.count(), 1)

    def test_facility_owner_attributes(self):
        """Test the facility owner attributes."""
        facility_owner = FacilityOwner(first_name='Jane', last_name='Doe', username='janedoe', email='janedoe@gmail.com')
        db.session.add(facility_owner)
        db.session.commit()

        saved_owner = FacilityOwner.query.first()
        self.assertEqual(saved_owner.first_name, 'Jane')
        self.assertEqual(saved_owner.last_name, 'Doe')
        self.assertEqual(saved_owner.username, 'janedoe')
        self.assertEqual(saved_owner.email, 'janedoe@gmail.com')

    # ---------- Review Model Tests ----------
    def test_create_review(self):
        """Test creating a review."""
        user = User(first_name='Alice', last_name='Smith', email='alice@example.com')
        facility = Facility(name='Happy Paws')
        db.session.add(user)
        db.session.add(facility)
        db.session.commit()

        review = Review(user_id=user.id, facility_id=facility.id, rating=5, comment='Great facility!')
        db.session.add(review)
        db.session.commit()

        self.assertEqual(Review.query.count(), 1)

    def test_review_attributes(self):
        """Test the review attributes."""
        user = User(first_name='Alice', last_name='Smith', email='alice@example.com')
        facility = Facility(name='Happy Paws')
        db.session.add(user)
        db.session.add(facility)
        db.session.commit()

        review = Review(user_id=user.id, facility_id=facility.id, rating=5, comment='Great facility!')
        db.session.add(review)
        db.session.commit()

        saved_review = Review.query.first()
        self.assertEqual(saved_review.rating, 5)
        self.assertEqual(saved_review.comment, 'Great facility!')

    def test_create_user_with_review(self):
        """Test that a user and associated review can be created."""
        user = User(first_name='Mark', last_name='Johnson', email='mark@example.com')
        facility = Facility(name='Pet Lovers')
        db.session.add(user)
        db.session.add(facility)
        db.session.commit()

        review = Review(user_id=user.id, facility_id=facility.id, rating=4, comment='Nice service.')
        db.session.add(review)
        db.session.commit()

        saved_review = Review.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(saved_review)

    def test_user_deletion_removes_reviews(self):
        """Test that deleting a user removes their reviews."""
        user = User(first_name='Mark', last_name='Johnson', email='mark@example.com')
        facility = Facility(name='Pet Lovers')
        db.session.add(user)
        db.session.add(facility)
        db.session.commit()

        review = Review(user_id=user.id, facility_id=facility.id, rating=4, comment='Nice service.')
        db.session.add(review)
        db.session.commit()

        self.assertIsNotNone(Review.query.filter_by(user_id=user.id).first())

        db.session.delete(user)
        db.session.commit()
        
        deleted_review = Review.query.filter_by(user_id=user.id).first()
        self.assertIsNone(deleted_review)


if __name__ == '__main__':
    unittest.main()
