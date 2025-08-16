'''All models for the application are stored in this file'''

from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    '''Load the user by id'''
    return User.query.get(int(id))


# Base user model for both dog owners and facility owners
# Contains all the neccesary user attributes
# Relationships User ------> Bookings

class User(UserMixin, db.Model):
    '''Define the User model'''
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone_number = db.Column(db.String(64))
    location = db.Column(db.String(64))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    about = db.Column(db.Text)
    skills_and_qualifications = db.Column(db.Text)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    user_type = db.Column(db.String(64))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpeg')
    bookings = db.relationship('Booking', back_populates='user')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def set_password(self, password):
        '''Set the password for the user'''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''Check the password for the user'''
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        '''Define the string representation for the User model'''
        return '<User {} is a {}>'.format(self.first_name, self.user_type)



# DogOwner inherits from the user for all the attributes
# Relationships DogOwner -----> Dogs

class DogOwner(User):
    '''Dog owner model'''
    __mapper_args__ = {
        'polymorphic_identity': 'dog_owner'
    }

    __tablename__ = 'user'

    dogs = db.relationship('Dog', backref='owner', lazy='dynamic')

    def __repr__(self):
        '''Define the string representation for the DogOwner model'''
        return '<DogOwner {}>'.format(self.username)


# FacilityOwner inherits from the user for all the attributes
# Relationships FacilityOwner  ----->  Facilities
    

class FacilityOwner(User):
    '''Facility owner model'''
    __mapper_args__ = {
        'polymorphic_identity': 'facility_owner'
    }

    __tablename__ = 'user'

    facilities = db.relationship('Facility', backref='owner', lazy='dynamic')

    def __repr__(self):
        '''Define the string representation for the FacilityOwner model'''
        return '<FacilityOwner {}>'.format(self.username)

# Dog Model 

class Dog(db.Model):
    '''Dog model'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    breed = db.Column(db.String(64))
    age = db.Column(db.Integer)
    size = db.Column(db.String(64))
    weight = db.Column(db.Float)
    sex = db.Column(db.String(64))
    image_file = db.Column(db.String(20), default='default_dog.jpg')
    emegergency_contact = db.Column(db.String(64))
    feeding_instructions = db.Column(db.Text)
    medications = db.Column(db.Text)
    special_needs = db.Column(db.Text)
    vet_name = db.Column(db.String(64))
    vet_phone = db.Column(db.String(64))
    vet_address = db.Column(db.String(64))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        '''Define the string representation for the Dog model'''
        return '<Dog {}>'.format(self.name)
    
class Facility(db.Model):
    '''Facility model'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(64))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    daycare = db.Column(db.Boolean)
    boarding = db.Column(db.Boolean)
    amenities = db.Column(db.Text)
    services = db.Column(db.Text)
    about = db.Column(db.Text)
    operating_hours = db.Column(db.String(64))
    contact_phone = db.Column(db.String(64))
    contact_email = db.Column(db.String(120))
    pricing = db.Column(db.String(64))
    capacity = db.Column(db.Integer)
    rating = db.Column(db.Float)
    emergency_transport = db.Column(db.Boolean)
    completed_bookings = db.Column(db.Integer, default=0)
    repeated_bookings = db.Column(db.Integer, default=0)
    repeated_customers = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0)
    photos = db.relationship('FacilityPhoto', backref='facility', lazy='dynamic')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookings = db.relationship('Booking', back_populates='facility')
    reviews = db.relationship('Review', backref='facility', lazy='dynamic')

    def __repr__(self):
        '''Define the string representation for the Facility model'''
        return '<Facility {}>'.format(self.name)
    
class FacilityPhoto(db.Model):
    '''Facility photo model'''
    id = db.Column(db.Integer, primary_key=True)
    photo_path = db.Column(db.String(255))
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'), nullable=False)


class Review(db.Model):
    '''Facility review model'''
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float)
    comment = db.Column(db.Text)
    response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'))
    
    

class Booking(db.Model):
    '''Booking model'''
    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(64))
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(64), default='pending')
    daycare = db.Column(db.String(64))
    boarding = db.Column(db.String(64))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    issued_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='bookings')
    number_of_dogs = db.Column(db.Integer)
    facility_id = db.Column(db.Integer, db.ForeignKey('facility.id'))
    facility = db.relationship('Facility', back_populates='bookings') 


    def update_status(self):
        '''Update the status to ongoing if the start date has arrived'''
        if self.check_in.date() <= datetime.now().date():
            self.status = 'ongoing'

    def __repr__(self):
        '''Define the string representation for the Booking model'''
        return '<Booking was created by {}>'.format(self.user.first_name)