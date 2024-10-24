'''All forms are defined here.'''

import requests
import datetime
from app import geolocator
from app.models import User, Facility
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, AnyOf


#--------------------LOGIN FORMS--------------------

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
        
    # def validate_location(self, location):
    #     '''Check if location is valid or exists'''
    #     if not location.data:
    #         raise ValidationError('Please enter a location')
        
    #     location = geolocator.geocode(location.data)
    #     if not location:
    #         raise ValidationError('Invalid location. Please enter a valid location')
    
    
class FacilityOwnerRegistrationForm(FlaskForm):
    '''Registration form for facility owners'''
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    # phone_number = StringField('Phone', validators=[DataRequired(), Length(max=10)])
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
    street = StringField('Street', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    contact_phone = StringField('Phone', validators=[DataRequired(), Length(max=10)])
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
    facility = StringField('Facility Name', validators=[DataRequired()])
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    notes = TextAreaField('Extra Information (optional)')
    daycare = BooleanField('Daycare')
    boarding = BooleanField('Boarding')
    number_of_dogs = SelectField('Number of Dogs', choices=[('Select number of dogs', 'Select number of dogs'),('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], validators=[DataRequired()])
    submit = SubmitField('Book Now')

    def validate_facility(self, facility):
        '''Check if facility exists'''
        facility = Facility.query.filter_by(name=facility.data).first()
        if not facility:
            raise ValidationError('Facility does not exist. Please enter a valid facility name')
        
    def validate_check_in(self, check_in):
        '''Check if check-in date is valid'''
        if check_in.data < datetime.date.today():
            raise ValidationError('Check-in date cannot be in the past')
        
    def validate_check_out(self, check_out):
        '''Check if check-out date is valid'''
        if check_out.data < datetime.date.today():
            raise ValidationError('Check-out date cannot be in the past')
        
        if check_out.data < self.check_in.data:
            raise ValidationError('Check-out date cannot be before check-in date')
        
    def validate_number_of_dogs(self, number_of_dogs):
        '''Check if number of dogs is valid'''
        if number_of_dogs.data == 'Select number of dogs':
            raise ValidationError('Please select the number of dogs')
        
    def validate_daycare(self, daycare):
        '''Check if daycare or boarding is selected'''
        if not daycare.data and not self.boarding.data:
            raise ValidationError('Please select either daycare or boarding')
        

#---------------UPDATE USER PROFILE FORM-----------------

class UpdateUserProfileForm(FlaskForm):
    '''Update user profile form'''
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    phone_number = StringField('Phone', validators=[DataRequired(), Length(max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = StringField('Location', validators=[DataRequired()])
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
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
    
    def validate_username(self, username):
        '''Validate Username'''
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Username is already taken. Please use a different username')
            

class UpdateFacilityOwnerProfileForm(FlaskForm):
    '''Update facility owner profile form'''
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    about = TextAreaField('About')
    skills_and_qualifications = TextAreaField('Skills and Qualifications')
    phone_number = StringField('Phone', validators=[DataRequired(), Length(max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Profile')

    def validate_email(self, email):
        '''Validate the email'''
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Email is already taken. Please use a different email address.')
            
    def validate_username(self, username):
        '''Validate the username'''
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Username is already taken. Please use a different username')
    
    def validate_location(self, location):
        '''Validate user location'''
        if not location.data:
            raise ValidationError('Please enter a location')
        
        location = geolocator.geocode(location.data)
        if not location:
            raise ValidationError('Invalid location. Please enter a valid location')
            



#-----------------UPDATE FACILITY PROFILE FORM-----------------
            
class UpdateFacilityProfileForm(FlaskForm):
    '''Update facility profile form'''
    name = StringField('Facility Name', validators=[DataRequired()])
    location = StringField('Facility Location', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    contact_phone = StringField('Phone', validators=[DataRequired(), Length(max=10)])
    contact_email = StringField('Email', validators=[DataRequired(), Email()])
    pricing = StringField('Pricing')
    daycare = BooleanField('Daycare')
    boarding = BooleanField('Boarding')
    capacity = StringField('Capacity')
    services = TextAreaField('Services')
    about = TextAreaField('About')
    amenities = TextAreaField('Amenities')
    operating_hours = StringField('Operating Hours')
    photos = FileField('Upload Facility Photos', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
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


#-----------------SET LOCATION FORM-----------------
    
class SetLocationForm(FlaskForm):
    '''Set Location form'''

    street = StringField('Street', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    submit = SubmitField('Save Location')