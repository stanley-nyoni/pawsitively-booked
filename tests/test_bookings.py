import unittest
from datetime import datetime, timedelta
from app import app, db
from app.models import User, Facility, Booking

class BookingModelTestCase(unittest.TestCase):
    def setUp(self):
        '''Set up the test client and database'''
        app.config.from_object('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user and facility
        self.user = User(first_name='Test', last_name='User', email='test@example.com')
        self.facility = Facility(name='Test Facility', location='Test Location', capacity=50)
        db.session.add(self.user)
        db.session.add(self.facility)
        db.session.commit()

    def tearDown(self):
        '''Tear down the test client and database'''
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_booking(self):
        '''Test that a booking can be created successfully.'''
        check_in = datetime.utcnow()
        check_out = check_in + timedelta(days=1)
        booking = Booking(
            booking_code='ABC123',
            check_in=check_in,
            check_out=check_out,
            notes='This is a test booking.',
            issued_by=self.user.id,
            facility_id=self.facility.id,
            number_of_dogs=2
        )
        db.session.add(booking)
        db.session.commit()

        saved_booking = Booking.query.first()
        self.assertIsNotNone(saved_booking)
        self.assertEqual(saved_booking.booking_code, 'ABC123')
        self.assertEqual(saved_booking.notes, 'This is a test booking.')
        self.assertEqual(saved_booking.status, 'pending')  # Default status
        self.assertEqual(saved_booking.number_of_dogs, 2)

    def test_booking_user_relationship(self):
        '''Test the relationship between Booking and User.'''
        booking = Booking(
            booking_code='REL123',
            check_in=datetime.utcnow(),
            check_out=datetime.utcnow() + timedelta(days=2),
            issued_by=self.user.id,
            facility_id=self.facility.id,
            number_of_dogs=1
        )
        db.session.add(booking)
        db.session.commit()

        self.assertEqual(booking.user, self.user)
        self.assertIn(booking, self.user.bookings)

    def test_booking_facility_relationship(self):
        '''Test the relationship between Booking and Facility.'''
        booking = Booking(
            booking_code='FAC456',
            check_in=datetime.utcnow(),
            check_out=datetime.utcnow() + timedelta(days=3),
            issued_by=self.user.id,
            facility_id=self.facility.id,
            number_of_dogs=3
        )
        db.session.add(booking)
        db.session.commit()

        self.assertEqual(booking.facility, self.facility)
        self.assertIn(booking, self.facility.bookings)

    def test_default_values(self):
        '''Test the default values for status and timestamps.'''
        booking = Booking(
            booking_code='DEF789',
            check_in=datetime.utcnow(),
            check_out=datetime.utcnow() + timedelta(days=1),
            issued_by=self.user.id,
            facility_id=self.facility.id,
            number_of_dogs=1
        )
        db.session.add(booking)
        db.session.commit()

        self.assertEqual(booking.status, 'pending')  # Default status
        self.assertIsNotNone(booking.created_at)
        self.assertIsNotNone(booking.updated_at)



if __name__ == '__main__':
    unittest.main()
