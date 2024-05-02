'''All forms are defined here.'''

import requests
from app import geolocator
from app.models import User
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, AnyOf


#--------------------LOG IN FORMS--------------------

class DogOwnerLoginForm(FlaskForm):
    '''Form for dog owner login.'''
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class FacilityOwnerLoginForm(FlaskForm):
    '''Form for facility owner login.'''
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


#--------------------USER REGISTRATION FORMS--------------------

class DogOwnerRegistrationForm(FlaskForm):
    '''Registration form for dog owners'''
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
        
    def validate_email(self, email):
        '''Validate the email'''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is already taken. Please use a different email address.')

    def validate_username(self, username):
        '''Validate the username'''
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is already taken. Please use a different username')
        
    def validate_location(self, location):
        '''Check if location is valid or exists'''
        if not location.data:
            raise ValidationError('Please enter a location')
        
        location = geolocator.geocode(location.data)
        if not location:
            raise ValidationError('Invalid location. Please enter a valid location')
    
    
class FacilityOwnerRegistrationForm(FlaskForm):
    '''Registration form for facility owners'''
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

        
    def validate_email(self, email):
        '''Validate the email'''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is already taken. Please use a different email address.')

    def validate_username(self, username):
        '''Validate the username'''
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is already taken. Please use a different username')


#--------------------FACILITY REGISTRATION FORM--------------------

class FacilityRegistrationForm(FlaskForm):
    '''Register Facility form'''
    name = StringField('Facility Name', validators=[DataRequired()])
    location = StringField('Facility Location', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    contact_phone = StringField('Phone', validators=[DataRequired()])
    contact_email = StringField('Email', validators=[DataRequired(), Email()])
    daycare = BooleanField('Daycare')
    boarding = BooleanField('Boarding')
    submit = SubmitField('Register Facility')

    def validate_location(self, location):
        '''Check if location is valid or exists'''
        if not location.data:
            raise ValidationError('Please enter a location')
        
        location = geolocator.geocode(location.data)
        if not location:
            raise ValidationError('Invalid location. Please enter a valid location')


#---------------------DOG REGISTRATION FORM-----------------------

class DogRegistrationForm(FlaskForm):
    '''Dog registration form'''
    name = StringField('Dog Name', validators=[DataRequired()])
    breed = StringField('Breed', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    size = SelectField('Size', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('giant', 'Giant')], validators=[DataRequired()])
    submit = SubmitField('Register Dog')



#----------------------UPDATE DOG PROFILE------------------------
    
class UpdateDogProfileForm(FlaskForm):
    '''Update your dogs profile'''
    name = StringField('Dog Name', validators=[DataRequired()])
    breed = StringField('Breed', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    size = SelectField('Size', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('giant', 'Giant')], validators=[DataRequired()])
    weight = StringField('Weight')
    sex = SelectField('Sex', choices=[('unfixed_male', 'Unfixed Male'), ('unfixed_female', 'Unfixed Female'), ('neutered_male', 'Neutered Male'), ('spayed_female', 'Spayed Female')], validators=[DataRequired()])
    emegergency_contact = StringField('Emergency Contact')
    feeding_instructions = TextAreaField('Feeding Instructions')
    medications = TextAreaField('Medications')
    special_needs = TextAreaField('Special Needs')
    vet_name = StringField('Vet Name')
    vet_phone = StringField('Vet Contact')
    submit = SubmitField('Update Profile')


#----------------------BOOKING FORM-----------------------

class BookingForm(FlaskForm):
    '''Booking form'''
    facility = StringField('Facility', validators=[DataRequired()])
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    daycare = BooleanField('Daycare')
    boarding = BooleanField('Boarding')
    number_of_dogs = SelectField('Number of Dogs', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], validators=[DataRequired()])
    submit = SubmitField('Book')


#---------------UPDATE USER PROFILE FORM-----------------

class UpdateUserProfileForm(FlaskForm):
    '''Update user profile form'''
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

    def validate_location(self, location):
        '''Check if location is valid or exists'''
        if not location.data:
            raise ValidationError('Please enter a location')
        
        location = geolocator.geocode(location.data)
        if not location:
            raise ValidationError('Invalid location. Please enter a valid location')
        
    def validate_email(self, email):
        '''Validate the email'''
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Email is already taken. Please use a different email address.')


#-----------------UPDATE FACILITY PROFILE FORM-----------------
            
class UpdateFacilityProfileForm(FlaskForm):
    '''Update facility profile form'''
    name = StringField('Facility Name', validators=[DataRequired()])
    location = StringField('Facility Location', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    contact_phone = StringField('Phone', validators=[DataRequired()])
    contact_email = StringField('Email', validators=[DataRequired(), Email()])
    pricing = StringField('Pricing')
    daycare = BooleanField('Daycare')
    boarding = BooleanField('Boarding')
    amenities = TextAreaField('Amenities')
    operating_hours = StringField('Operating Hours')
    submit = SubmitField('Update Profile')

    def validate_location(self, location):
        '''Check if location is valid or exists'''
        if not location.data:
            raise ValidationError('Please enter a location')
        
        location = geolocator.geocode(location.data)
        if not location:
            raise ValidationError('Invalid location. Please enter a valid location')

#-----------------SEARCH FORM-----------------

class SearchFacilityForm(FlaskForm):
    '''Search facility form'''
    location = StringField('Location', validators=[DataRequired()])
    daycare = BooleanField('Daycare')
    boarding = BooleanField('Boarding')
    submit = SubmitField('Search')


