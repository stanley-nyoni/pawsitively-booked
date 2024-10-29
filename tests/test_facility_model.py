import unittest
from app import app, db
from app.models import User, Facility

class FacilityModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.owner = User(username='facilityowner', email='owner@example.com')
        db.session.add(self.owner)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_facility(self):
        facility = Facility(name='Dog Paradise', location='123 Pet Lane', owner_id=self.owner.id)
        db.session.add(facility)
        db.session.commit()
        retrieved_facility = Facility.query.filter_by(name='Dog Paradise').first()
        self.assertIsNotNone(retrieved_facility)

    def test_update_facility(self):
        facility = Facility(name='Dog World', location='456 Bark Avenue', owner_id=self.owner.id)
        db.session.add(facility)
        db.session.commit()
        facility.location = '789 Paw Street'
        db.session.commit()
        updated_facility = Facility.query.filter_by(name='Dog World').first()
        self.assertEqual(updated_facility.location, '789 Paw Street')

    def test_delete_facility(self):
        facility = Facility(name='Pet Haven', owner_id=self.owner.id)
        db.session.add(facility)
        db.session.commit()
        db.session.delete(facility)
        db.session.commit()
        self.assertIsNone(Facility.query.filter_by(name='Pet Haven').first())

if __name__ == '__main__':
    unittest.main()
