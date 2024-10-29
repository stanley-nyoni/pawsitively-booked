import unittest
from app import app, db
from app.models import User, Dog

class DogModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.owner = User(username='dogowner', email='owner@example.com')
        db.session.add(self.owner)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_dog(self):
        dog = Dog(name='Max', breed='Bulldog', owner_id=self.owner.id)
        db.session.add(dog)
        db.session.commit()
        retrieved_dog = Dog.query.filter_by(name='Max').first()
        self.assertIsNotNone(retrieved_dog)

    def test_update_dog(self):
        dog = Dog(name='Rocky', breed='Labrador', owner_id=self.owner.id)
        db.session.add(dog)
        db.session.commit()
        dog.breed = 'Golden Retriever'
        db.session.commit()
        updated_dog = Dog.query.filter_by(name='Rocky').first()
        self.assertEqual(updated_dog.breed, 'Golden Retriever')

    def test_delete_dog(self):
        dog = Dog(name='Buddy', breed='Beagle', owner_id=self.owner.id)
        db.session.add(dog)
        db.session.commit()
        db.session.delete(dog)
        db.session.commit()
        self.assertIsNone(Dog.query.filter_by(name='Buddy').first())

if __name__ == '__main__':
    unittest.main()
