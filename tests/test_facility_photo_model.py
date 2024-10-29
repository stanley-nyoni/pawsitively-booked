import unittest
from app import app, db
from app.models import Facility, FacilityPhoto

class FacilityPhotoModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.facility = Facility(name='Paws Resort')
        db.session.add(self.facility)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_photo(self):
        photo = FacilityPhoto(photo_path='photos/image1.jpg', facility_id=self.facility.id)
        db.session.add(photo)
        db.session.commit()
        retrieved_photo = FacilityPhoto.query.first()
        self.assertIsNotNone(retrieved_photo)

    def test_delete_photo(self):
        photo = FacilityPhoto(photo_path='photos/image2.jpg', facility_id=self.facility.id)
        db.session.add(photo)
        db.session.commit()
        db.session.delete(photo)
        db.session.commit()
        self.assertIsNone(FacilityPhoto.query.first())

if __name__ == '__main__':
    unittest.main()
