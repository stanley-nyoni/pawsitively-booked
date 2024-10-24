# Module - app/routes.py


from sqlalchemy import and_
from geopy.distance import geodesic
import requests, secrets, os
from datetime import datetime
from urllib.parse import urlsplit
from urllib.parse import quote
from app import app, db, mail, Message
from werkzeug.utils import secure_filename
from app.models import User, Facility, Dog, DogOwner, FacilityOwner, Booking, FacilityPhoto
from flask import render_template, redirect, flash, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import FacilityOwnerRegistrationForm, FacilityRegistrationForm, DogRegistrationForm
from app.forms import DogOwnerLoginForm, FacilityOwnerLoginForm, DogOwnerRegistrationForm, UpdateFacilityOwnerProfileForm 
from app.forms import SearchFacilityForm, BookingForm, UpdateDogProfileForm, UpdateUserProfileForm, UpdateFacilityProfileForm
from app.forms import SetLocationForm


OWM_API_KEY = app.config['OWM_API_KEY']
GO_MAPS_API_KEY = app.config['GO_MAPS_API_KEY']


# --------------------HELPER FUNCTIONS--------------------

def get_location(location):
    '''Get the geolocation of the location'''
    geocode_url = f"https://maps.gomaps.pro/maps/api/geocode/json?address={quote(location)}&key={GO_MAPS_API_KEY}&limit=1"
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            latitude = data['results'][0]['geometry']['location']['lat']
            longitude = data['results'][0]['geometry']['location']['lng']
            return latitude, longitude
        else:
            flash('No coordinates found for this location.', 'danger')
            return None
    else:
        flash('Failed to get coordinates. Please try again.', 'danger')
        return None
    

# Generating the greeting message for the user based on the current time.
# The greeting message will be displayed on the dashboard page.

def get_greeting():
    '''Get a greeting text for user'''
    current_time = datetime.now()
    current_hour = current_time.hour
    if current_hour < 12:
        return 'Good morning'
    elif current_hour < 18:
        return 'Good afternoon'
    else:
        return 'Good evening'
    
def generate_welcoming_msg():
    '''Generate a welcoming message for the user'''
    greeting = get_greeting()
    if not current_user.first_name:
        return greeting
    msg = f'{greeting}, {current_user.first_name}!'
    return msg



# Sending email notification function
def send_notification(email, subject, template):
    '''Send email notification'''
    msg = Message(subject,
                  sender='pawsitivelybookings@gmail.com',
                  html=template,
                    recipients=[email])
    
    mail.send(msg)


def calculate_distance(facility, user):
    '''Calculate the distance between the facility and the user'''
    user_location = (user.latitude, user.longitude)
    facility_location = (facility.latitude, facility.longitude)
    distance = geodesic(user_location, facility_location).kilometers
    return round(distance, 2)

# --------------------INDEX--------------------


# The home page for the application.
# Displays the landing page if the user is not logged in.
# Redirects to the appropriate dashboard if the user is logged in.
    
@app.route('/')
@app.route('/index')
def index():
    '''Define the view function for the index page'''
    form = SearchFacilityForm()

    page = request.args.get('page', 1, type=int)
    facilities = Facility.query.paginate(page=page, per_page=5)

    # Calculate distnce from current user to each facility

    if current_user.is_authenticated:
        if current_user.location:
            for facility in facilities.items:
                facility.distance = calculate_distance(facility, current_user)


    return render_template('index.html', form=form, facilities=facilities)


# --------------------CUSTOM ERROR PAGES--------------------

@app.errorhandler(404)
def page_not_found(e):
    '''Define the view function for the 404 error page'''
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    '''Define the view function for the 500 error page'''
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    '''Define the view function for the 403 error page'''
    return render_template('errors/403.html'), 403

# --------------------DASHBOARDS--------------------


# The dashboard page for the application.
# Displays the dashboard page for the dog owner if the user is a dog owner.

@app.route('/dashboard/dog_owner')
@login_required
def dashboard_dog_owner():
    '''Define the view function for the dashboard page'''
    dogs = current_user.dogs.all()                                   

    upcoming_bookings = Booking.query.filter(Booking.issued_by == current_user.id,
                                              Booking.status.in_(['accepted', 'pending']),
                                                Booking.check_in > datetime.now()).all()
    for booking in upcoming_bookings:
        booking.check_in_formatted = booking.check_in.strftime('%B %d, %Y')
        booking.check_out_formatted = booking.check_out.strftime('%B %d, %Y')

    history_bookings = Booking.query.filter(Booking.issued_by == current_user.id,
                                           Booking.status.in_(['completed', 'cancelled', 'declined', 'expired']),
                                              Booking.check_out > datetime.now()).all()
    for booking in history_bookings:
        booking.check_in_formatted = booking.check_in.strftime('%B %d, %Y')
        booking.check_out_formatted = booking.check_out.strftime('%B %d, %Y')

    ongoing_bookings = Booking.query.filter(Booking.issued_by == current_user.id,
                                             Booking.status == 'ongoing',
                                               Booking.check_in <= datetime.now(),
                                               Booking.check_out > datetime.now()).all()
    
    for booking in ongoing_bookings:
        booking.check_in_formatted = booking.check_in.strftime('%B %d, %Y')
        booking.check_out_formatted = booking.check_out.strftime('%B %d, %Y')

    length = {
        'upcoming_count': len(upcoming_bookings),
        'history_count': len(history_bookings),
        'ongoing_count': len(ongoing_bookings)
    }
    
    return render_template('dog_owner/dashboard.html',dogs=dogs,
                            greeting=generate_welcoming_msg(),
                            upcoming_bookings=upcoming_bookings,
                              history_bookings=history_bookings,
                                ongoing_bookings=ongoing_bookings,
                                length=length)


# The dashboard page for the application.
# Displays the dashboard page for the facility owner if the user is a facility owner.

@app.route('/dashboard/facility_owner')
@login_required
def dashboard_facility_owner():
    '''Define the view function for the dashboard page'''

    facilities_with_bookings = []
    facilities = current_user.facilities.all()
    for facility in facilities:
        booking_requests = Booking.query.filter(Booking.facility_id == facility.id,
                                                Booking.status == 'pending').all()
        
        for booking in booking_requests:
            booking.check_in_formatted = booking.check_in.strftime('%B %d, %Y')
            booking.check_out_formatted = booking.check_out.strftime('%B %d, %Y')

        upcoming_bookings = Booking.query.filter(Booking.facility_id == facility.id,
                                                  Booking.status == 'accepted',
                                                    Booking.check_in > datetime.now()).all()
        for booking in upcoming_bookings:
            booking.check_in_formatted = booking.check_in.strftime('%B %d, %Y')
            booking.check_out_formatted = booking.check_out.strftime('%B %d, %Y')

        ongoing_bookings = Booking.query.filter(Booking.facility_id == facility.id,
                                                    Booking.status == 'ongoing',
                                                    Booking.check_in <= datetime.now(),
                                                    Booking.check_out > datetime.now()).all()
        for booking in ongoing_bookings:
            booking.check_in_formatted = booking.check_in.strftime('%B %d, %Y')
            booking.check_out_formatted = booking.check_out.strftime('%B %d, %Y')
        
        history_bookings = Booking.query.filter(Booking.facility_id == facility.id,
                                                Booking.status.in_(['completed', 'cancelled', 'declined', 'expired']),
                                                Booking.check_out > datetime.now()).all()
        for booking in history_bookings:
            booking.check_in_formatted = booking.check_in.strftime('%B %d, %Y')
            booking.check_out_formatted = booking.check_out.strftime('%B %d, %Y')

        facilities_with_bookings.append({
            'facility': facility,
            'booking_requests': booking_requests,
            'upcoming_bookings': upcoming_bookings,
            'ongoing_bookings': ongoing_bookings,
            'history_bookings': history_bookings
        })

    return render_template('facility_owner/dashboard.html',
                            facilities=facilities,
                              facilities_with_bookings=facilities_with_bookings,
                                greeting=generate_welcoming_msg())


#---------------UPDATE BOOKING STATUS-------------


# Update bookings
# This automatically update the bookings
# Visit models

@app.route('/update_bookings')
def update_bookings():
    '''Update the booking status'''

    ongoing_bookings = Booking.query.filter(Booking.check_in <= datetime.now(),
                                    Booking.status.in_(['accepted', 'pending'])).all()
    for booking in ongoing_bookings:
        booking.update_status()

    expired_bookings = Booking.query.filter(Booking.check_out <= datetime.now(),
                                    Booking.status.in_(['accepted', 'pending'])).all()
    for booking in expired_bookings:
        booking.status = 'expired'


    completed_bookings = Booking.query.filter(Booking.check_out <= datetime.now(),
                                    Booking.status == 'ongoing').all()
    
    for booking in completed_bookings:
        booking.status = 'completed'
        if booking.facility.completed_bookings:
            booking.facility.completed_bookings += 1
        else:
            booking.facility.completed_bookings = 1

        send_notification(booking.user.email,
                          'Your Booking is Now Complete - Thank you!',
                          template=f"<p> Hi {booking.user.first_name}, </p> <p>We hope your furry friend enjoyed their stay with us! We are writing to let you know that your booking at {booking.facility.name} has been successfully completed. </p> <p> Here are the datails of your booking: </p> <p> <b>Check-in: </b> {booking.check_in} </p> <p> <b>Check-out: </b> {booking.check_out} </p> <p> <b>Number of dogs: </b>{booking.number_of_dogs} </p><p><b> Facility: </b>{booking.facility.name} </p><p><b>Total Stay Duration: </b> {booking.total_days} days </p>  <p>We would love to hear about your experience. Your feedback helps us improve and continue providing the best care for your beloved pet.</p> <p> Thank you for using our services. We look forward to seeing you again soon! </p> <p> Best regards, </p> <p> The PawsitivelyBooked Team </p>")

        
        send_notification(booking.facility.owner.email,
                            'Booking Completion Notification - Booking ID #{}'.format(booking.id),
                               template=f"<p> Hi {booking.facility.owner.first_name}, </p> <p> This is a notification to inform you that the booking with ID #{booking.id} for {booking.user.first_name }at your facility, {booking.facility.name}, has been successfully completed as of {booking.check_out}</p> <p> Here are the details of the booking: </p> <p> <b>Check-in: </b> {booking.check_in} </p> <p> <b>Check-out: </b> {booking.check_out} </p> <p> <b>Number of dogs: </b>{booking.number_of_dogs} </p><p><b> Facility: </b>{booking.facility.name} </p><p><b>Total Stay Duration: </b> {booking.total_days} days </p> <p> Thank you for your attention to this booking. Your dedication to providing excellent service is greatly appreciated. </p> <p> Best regards, </p> <p> The PawsitivelyBooked Team </p>")

    # Commit the changes to the database
    db.session.commit()

    return 'Bookings updated successfully.'


# --------------------REDIRECT DASHBOARDS--------------------

# Redirect to the appropriate dashboard based on user type
# If the user is not authenticated, redirect to the login page.

@app.route('/dashboard')
def redirect_dashboard():
    '''Redirect to the appropriate dashboard based on user type'''
    if current_user.is_authenticated:
        if current_user.user_type == 'dog_owner':
            return redirect(url_for('dashboard_dog_owner'))
        elif current_user.user_type == 'facility_owner':
            return redirect(url_for('dashboard_facility_owner'))
    return redirect(url_for('login'))

#--------------------FAQs--------------------

# The FAQs page for the application.
# Displays the FAQs page.

@app.route('/faqs')
def faqs():
    '''Define the view function for the FAQs page'''
    return render_template('faqs.html')



#--------------------FEATURES--------------------

# The features page for the application.
# Displays the features page.

@app.route('/features')
def features():
    '''Define the view function for the features page'''
    return render_template('features.html')

# --------------------LOGINS--------------------

# User login, base endpoint for both pet owners and facility owners
# Diiferent links to each target login

@app.route('/login')
def login():
    '''Define the view function for the login page'''
    return render_template('login.html')


@app.route('/login/dog_owner', methods=['GET', 'POST'])
def dog_owner_login():
    '''Define the view function for the dog owner login page'''
    if current_user.is_authenticated:
        return redirect('/index')
    form = DogOwnerLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data) or user.user_type != 'dog_owner':
            flash('Invalid email or password', 'danger')
            return redirect('/login/dog_owner')
        
        login_user(user, remember=form.remember_me.data)
        flash("You're now logged in.", "success")
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('dashboard_dog_owner')
        return redirect(next_page)
    return render_template('dog_owner/login.html', form=form)


@app.route('/login/facility_owner', methods=['GET', 'POST'])
def facility_owner_login():
    '''Define the view function for the facility owner login page'''
    if current_user.is_authenticated:
        return redirect('/index')
    form = FacilityOwnerLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data) or user.user_type != 'facility_owner':
            flash('Invalid email or password', 'danger')
            return redirect('/login/facility_owner')
        
        login_user(user, remember=form.remember_me.data)
        flash("You're now logged in", "success")
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('dashboard_facility_owner')
        return redirect(next_page)
    return render_template('facility_owner/login.html', form=form)



# --------------------SIGNUPS--------------------

# User registration, base endpoint for both pet owners and facilitty owners

@app.route('/signup')
def signup():
    '''Define the view function for the signup page'''
    return render_template('signup.html')

@app.route('/signup/dog_owner', methods=['GET', 'POST'])
def signup_dog_owner():
    '''Define the view function for the signup page'''
    if current_user.is_authenticated:
        return redirect('/index')
    
    form = DogOwnerRegistrationForm()
    if form.validate_on_submit():
        user = DogOwner(first_name=form.first_name.data,
                     last_name=form.last_name.data,
                     username=form.username.data,
                    #    phone_number=form.phone_number.data,
                         email=form.email.data,
                        #  location=form.location.data,
                           user_type='dog_owner')
        
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Account successfully created. You can now login.', 'success')
        return redirect('/login/dog_owner')
    return render_template('dog_owner/registration.html', form=form)


@app.route('/signup/facility_owner', methods=['GET', 'POST'])
def signup_facility_owner():
    '''Define the view function for the signup page'''
    if current_user.is_authenticated:
        return redirect('/index')
    
    form = FacilityOwnerRegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('User already exists.', 'danger')
            return redirect('/signup/facility_owner')

        user = FacilityOwner(first_name=form.first_name.data,
                     last_name=form.last_name.data,
                     username=form.username.data,
                    #    phone_number=form.phone_number.data,
                         email=form.email.data,
                           user_type='facility_owner')
        
        # print(form.password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Account successfully created. You can now login.', 'success')
        return redirect('/login/facility_owner')
    return render_template('facility_owner/registration.html', form=form)



# --------------------FACILITY REGISTRATION--------------------


# Facility registration
# Fscility Owners only

@app.route('/facility_registration', methods=['GET', 'POST'])
@login_required
def facility_registration():
    '''Facility registration'''
    form = FacilityRegistrationForm()
    if current_user.is_authenticated:
        # form.contact_phone.data = current_user.phone_number
        form.contact_email.data = current_user.email

    if form.validate_on_submit():
        street = form.street.data
        city = form.city.data
        postal_code = form.postal_code.data
        country = form.country.data

        location = f'{street}, {city}, {postal_code}, {country}'
        coordinates = get_location(location)

        if not coordinates:
            return redirect(url_for('facility_registration'))
        
        latitude, longitude = coordinates
        facility = Facility(name=form.name.data,
                            description=form.description.data,
                            location=location,
                            latitude=latitude,
                            longitude=longitude,
                            contact_phone=form.contact_phone.data,
                            contact_email=form.contact_email.data,
                            daycare=form.daycare.data,
                            boarding=form.boarding.data,
                            owner=current_user)
        
        db.session.add(facility)
        db.session.commit()
        flash('Facility successfully registered.', 'success')
        return redirect(url_for('dashboard_facility_owner'))
    return render_template('facility_owner/register_facility.html', form=form)


# --------------------DOG REGISTRATION--------------------

# Dog profile registration for dog owners
# Create before any bookings

@app.route('/dog_registration', methods=['GET', 'POST'])
@login_required
def dog_registration():
    '''Define the view function for the dog registration page'''
    form = DogRegistrationForm()
    if form.validate_on_submit():
        dog = Dog(name=form.name.data,
                  breed=request.form['breed'],
                  age=form.age.data,
                  size=form.size.data,
                  owner=current_user)
        
        db.session.add(dog)
        db.session.commit()
        flash('Dog successfully registered.', 'success')
        return redirect(url_for('dashboard_dog_owner'))
    return render_template('dog_owner/add_new_dog.html', form=form)


# --------------------SEARCH FACILITY--------------------


# Search facilities not complete
# See forms.py

@app.route('/search_facility', methods=['GET', 'POST'])
def search_facility():
    '''Define the view function for the search facility page'''
    if request.method == 'POST':
        location = request.form.get('location')

        geocode_url = f'http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OWM_API_KEY}'
        response = requests.get(geocode_url)
        if response.status_code == 200:
            data = response.json()
            if data:
                latitude = data[0]['lat']
                longitude = data[0]['lon']

                facilities = Facility.query.filter_by(location=location).all()

                if not facilities:
                    flash('No facilities found in this location.', 'danger')
                    return redirect(url_for('search_facility'))
                
                facility_ids = [facility.id for facility in facilities]
                session['facilities'] = facility_ids
                return redirect(url_for('search_results'))
            else:
                flash('No coordinates found for this location.', 'danger')
                return redirect(url_for('search_facility'))
        else:
            flash('Failed to get coordinates. Please try again.', 'danger')
            return redirect(url_for('search_facility'))
    return render_template('dog_owner/home.html')


@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    '''Define the view function for the search results page'''
    facility_ids = session.get('facilities')

    if not facility_ids:
        return redirect(url_for('search_facility'))
    # Retrieve facilities from database using stored ids
    facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
    return render_template('dog_owner/search_results.html', facilities=facilities)


# --------------------BOOKING--------------------


# Create a booking - by dog owners

@app.route('/dog_owner/create_booking', methods=['GET', 'POST'])
@login_required
def create_booking():
    '''Define the view function for the create booking page'''
    form = BookingForm()
    if form.validate_on_submit():
        facility = Facility.query.filter_by(name=form.facility.data).first()
        if not facility:
            flash('Facility not found. Please try again.', 'danger')
            return redirect(url_for('create_booking'))
        
        booking = Booking(check_in=form.check_in.data,
                          check_out=form.check_out.data,
                          issued_by=current_user.id,
                          facility_id = facility.id,
                          daycare = form.daycare.data,
                          boarding = form.boarding.data,
                          number_of_dogs=form.number_of_dogs.data)
        
        db.session.add(booking)
        db.session.commit()
        flash('Booking successfully created.', 'success')

        check_in = booking.check_in.strftime('%B %d, %Y')
        check_out = booking.check_out.strftime('%B %d, %Y')

        # Send email notfications

        send_notification(
        booking.user.email,
        'Booking Created Successfully!',
        template=(
            f'<p> Hi {booking.user.first_name}, </p>'
            f'<p> You have successfully created a booking at {booking.facility.name} '
            f'.</p>'
            f'<p> <b>Check-in:</b> {check_in} </p>'
            f'<p> <b>Check-out:</b> {check_out} </p>'
            f'<p> <b>Number of dogs:</b> {booking.number_of_dogs} </p>'
            f'<p>Please log in and check your dahsboard for any information might not be correct.</p>'
            f'<p> Best regards, </p> <p> The PawsitivelyBooked Team </p>'
        )
        )

        send_notification(
        booking.facility.contact_email,
        f'New Booking Request - Booking ID #{booking.id}',
        template=(
            f'<p> Hi {booking.facility.owner.first_name},</p>'
            f'<p> You have recieved a new  booking for {booking.facility.name} with ID #{booking.id}. </p>'
            f'<p> <b>Check-in:</b> {check_in} </p>'
            f'<p> <b>Check-out:</b> {check_out} </p>'
            f'<p> <b>Number of dogs:</b> {booking.number_of_dogs} </p>'
            f'<p> Please check your dashboard for more details. </p>'
            f'<p> Best regards, </p> <p> The PawsitivelyBooked Team </p>'
        )
        )

        return redirect(url_for('dashboard_dog_owner'))
    elif request.method == 'GET':
        form.check_in.data = datetime.now()
        form.check_out.data = datetime.now()
        form.number_of_dogs.data = 'Select Number of Dogs'
        if current_user.user_type == 'facility_owner':
            form.facility.data = current_user.facilities.first().name
        
        if current_user.user_type == 'dog_owner':
            form.facility.choices = [(facility.name, facility.name) for facility in Facility.query.all()]

        # If the requests.args got the facility name, set the facility name in the form
        if request.args.get('facility_name'):
            form.facility.data = request.args.get('facility_name')

    return render_template('dog_owner/create_booking.html', form=form)

# --------------------VIEW BOOKING--------------------

@app.route('/dog_owner/view_booking/<int:booking_id>')
@login_required
def view_booking(booking_id):
    '''Define the view function for the view booking page'''
    dogs = current_user.dogs.all()
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
    check_in = booking.check_in.strftime('%B %d, %Y')
    check_out = booking.check_out.strftime('%B %d, %Y')
    created_at = booking.created_at.strftime('%B %d, %Y %I:%M %p')
    updated_at = booking.updated_at.strftime('%B %d, %Y %I:%M %p') 
    return render_template('dog_owner/view_booking.html', booking=booking, check_in=check_in, check_out=check_out, dogs=dogs, created_at=created_at, updated_at=updated_at)


# --------------------CANCEL BOOKING--------------------

@app.route('/dog_owner/cancel_booking/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def cancel_booking(booking_id):
    '''Define the view function for the cancel booking page'''
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard_dog_owner'))
    
    booking.updated_at = datetime.now()
    booking.status = 'cancelled'
    db.session.commit()
    flash('Booking successfully cancelled.', 'success')

    check_in = booking.check_in.strftime('%B %d, %Y')
    check_out = booking.check_out.strftime('%B %d, %Y')

        # Send email notfications

    send_notification(
    booking.user.email,
    'Booking Cancelled',
    template=(
        f'<p> Hi {booking.user.first_name}, </p>'
        f'<p> You have cancelled your booking {booking.facility.name} '
        f'.</p>'
        f'<p> <b>Check-in:</b> {check_in} </p>'
        f'<p> <b>Check-out:</b> {check_out} </p>'
        f'<p> <b>Number of dogs:</b> {booking.number_of_dogs} </p>'
        f'<p>Please log in and check your dahsboard for any information might not be correct.</p>'
        f'<p> Best regards, </p> <p> The PawsitivelyBooked Team </p>'
    )
    )

    send_notification(
    booking.facility.contact_email,
    f'Booking Canncelled - Booking ID #{booking.id}',
    template=(
        f'<p> Hi {booking.facility.owner.first_name},</p>'
        f'<p> This booking has been cancelled  Booking ID #{booking.id}. </p>'
        f'<p> <b>Check-in:</b> {check_in} </p>'
        f'<p> <b>Check-out:</b> {check_out} </p>'
        f'<p> <b>Number of dogs:</b> {booking.number_of_dogs} </p>'
        f'<p> Please check your dashboard for more details. </p>'
        f'<p> Best regards, </p> <p> The PawsitivelyBooked Team </p>'
    )
    )
    return redirect(url_for('dashboard_dog_owner'))


# --------------------DELETE BOOKING--------------------


@app.route('/dog_owner/delete_booking_history/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def delete_booking_history(booking_id):
    '''Define the view function for the cancel booking page'''
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Booking history not found.', 'danger')
        return redirect(url_for('dashboard_dog_owner'))
    
    db.session.delete(booking)
    db.session.commit()
    flash('Booking history successfully deleted.', 'success')
    return redirect(url_for('dashboard_dog_owner'))



#------------------VIEW DOG PROFILE--------------------

@app.route('/dog_owner/dog_profile', methods=['GET', 'POST'])
@login_required
def dog_profile():
    '''Define the view function for the dog profile page'''
    dogs = current_user.dogs.all()
    return render_template('dog_owner/dog_profile.html', dogs=dogs)

# --------------------UPDATE DOG PROFILE--------------------

@app.route('/dog_owner/update_dog_profile/<int:dog_id>', methods=['GET', 'POST'])
@login_required
def update_dog_profile(dog_id):
    '''Update dog profile with ID'''
    dog = Dog.query.get_or_404(dog_id) 
    form = UpdateDogProfileForm()

    if request.method == 'GET':
        form.name.data = dog.name
        form.breed.data = dog.breed
        form.age.data = str(dog.age)
        form.size.data = dog.size
        form.weight.data = str(dog.weight)
        form.emegergency_contact.data = dog.emegergency_contact
        form.feeding_instructions.data = dog.feeding_instructions
        form.medications.data = dog.medications
        form.special_needs.data = dog.special_needs
        form.vet_name.data = dog.vet_name
        form.vet_phone.data = dog.vet_phone

    if form.validate_on_submit():
        dog.name = form.name.data
        dog.breed = form.breed.data
        dog.age = int(form.age.data)
        dog.size = form.size.data
        dog.weight = float(form.weight.data)
        dog.emegergency_contact = form.emegergency_contact.data
        dog.feeding_instructions = form.feeding_instructions.data
        dog.medications = form.medications.data
        dog.special_needs = form.special_needs.data
        dog.vet_name = form.vet_name.data
        dog.vet_phone = form.vet_phone.data

        db.session.commit()
        flash('Dog profile successfully updated.', 'success')
        return redirect(url_for('dog_profile'))

    return render_template('dog_owner/update_dog_profile.html', form=form, dog=dog)



#---------------VIEW FACILITIES---------------

@app.route('/facility_owner/my_facilities', methods=['GET', 'POST'])
@login_required
def my_facilities():
    '''Define the view function for the my facilities page'''
    facilities = current_user.facilities.all()
    return render_template('facility_owner/facilities.html', facilities=facilities)


# Save facilitity photos function
def save_photos(form_photo):
    '''Save the photos'''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(secure_filename(form_photo.filename))
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/facility_images', picture_fn)
    form_photo.save(picture_path)

    return picture_fn

#-----------------UPDATE FACILITY PROFILE---------------------

@app.route('/facility_owner/update_facility_profile/<int:facility_id>', methods=['GET', 'POST'])
@login_required
def update_facility_profile(facility_id):
    '''Update facility profile with ID'''
    form = UpdateFacilityProfileForm()
    facility = Facility.query.get(facility_id)

    if form.validate_on_submit():
        changes_made = False
        if form.photos.data:
            for photo in request.files.getlist('photos'):
                if photo:
                    picture_file = save_photos(photo)
                    facility_photo = FacilityPhoto(facility_id=facility.id, photo_path=picture_file)
                    db.session.add(facility_photo)
                    flash('Photos successfully uploaded.', 'success')
                    
        if form.name.data != facility.name:
            facility.name = form.name.data
            changes_made = True
        if form.location.data != facility.location:
            facility.location = form.location.data
            changes_made = True
        if form.description.data != facility.description:
            facility.description = form.description.data
            changes_made = True
        if form.pricing.data != facility.pricing:
            facility.pricing = form.pricing.data
            changes_made = True
        if form.operating_hours.data != facility.operating_hours:
            facility.operating_hours = form.operating_hours.data
            changes_made = True
        if form.amenities.data != facility.amenities:
            facility.amenities = form.amenities.data
            changes_made = True
        if form.services.data != facility.services:
            facility.services = form.services.data
            changes_made = True
        if form.about.data != facility.about:
            facility.about = form.about.data
            changes_made = True
        if form.contact_phone.data != facility.contact_phone:
            facility.contact_phone = form.contact_phone.data
            changes_made = True
        if form.contact_email.data != facility.contact_email:
            facility.contact_email = form.contact_email.data
            changes_made = True
        if form.daycare.data != facility.daycare:
            facility.daycare = form.daycare.data
            changes_made = True
        if form.boarding.data != facility.boarding:
            facility.boarding = form.boarding.data
            changes_made = True

        if changes_made:
            db.session.commit()
            flash('Facility profile successfully updated.', 'success')
        return redirect(url_for('my_facilities'))
    elif request.method == 'GET':
        form.name.data = facility.name
        form.location.data = facility.location
        form.description.data = facility.description
        form.amenities.data = facility.amenities
        form.pricing.data = facility.pricing
        form.services.data = facility.services
        form.about.data = facility.about
        form.operating_hours.data = facility.operating_hours
        form.contact_phone.data = facility.contact_phone
        form.contact_email.data = facility.contact_email
        form.daycare.data = facility.daycare
        form.boarding.data = facility.boarding

    return render_template('facility_owner/update_facility.html', form=form, facility=facility)


# Save Picture Function

def save_picture(form_picture):
    '''Save the picture'''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/profile_pictures', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


#-----------------USER PROFILE---------------------

@app.route('/dog_owner/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    '''Define the view function for the user profile page'''
    form = UpdateUserProfileForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
            current_user.image_file = picture_file
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        current_user.location = form.location.data


        coordinates = get_location(current_user.location)
        if not coordinates:
            return redirect(url_for('user_profile'))
        
        current_user.latitude, current_user.longitude = coordinates
        
        db.session.commit()
        flash('Profile successfully updated.', 'success')
        return redirect(url_for('user_profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.username.data = current_user.username
        form.phone_number.data = current_user.phone_number
        form.location.data = current_user.location
        form.email.data = current_user.email

    image_file = url_for('static', filename='images/profile_pictures/' + current_user.image_file)
    
    return render_template('dog_owner/user_profile.html', form=form, image_file=image_file)


@app.route('/facility_owner/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile_facility_owner():
    '''Define the view function for the user profile page'''
    form = UpdateFacilityOwnerProfileForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
            current_user.image_file = picture_file
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.about = form.about.data
        current_user.skills_and_qualifications = form.skills_and_qualifications.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        current_user.location = form.location.data

        coordinates = get_location(current_user.location)
        if not coordinates:
            return redirect(url_for('user_profile_facility_owner'))
        
        current_user.longitude, current_user.latitude = coordinates

        # geocode_url = f'http://api.openweathermap.org/geo/1.0/direct?q={current_user.location}&limit=1&appid={OWM_API_KEY}'
        # response = requests.get(geocode_url)
        # if response.status_code == 200:
        #     data = response.json()
        #     if data:
        #         current_user.latitude = data[0]['lat']
        #         current_user.longitude = data[0]['lon']
        #     else:
        #         flash('No coordinates found for this location.', 'danger')
        #         return redirect(url_for('user_profile_facility_owner'))
        # else:
        #     flash('Failed to get coordinates. Please try again.', 'danger')
        #     return redirect(url_for('user_profile_facility_owner'))

        db.session.commit()
        flash('Profile successfully updated.', 'success')
        return redirect(url_for('user_profile_facility_owner'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.username.data = current_user.username
        form.about.data = current_user.about
        form.skills_and_qualifications.data = current_user.skills_and_qualifications
        form.phone_number.data = current_user.phone_number
        form.location.data = current_user.location
        form.email.data = current_user.email

    image_file = url_for('static', filename='images/profile_pictures/' + current_user.image_file)
    return render_template('facility_owner/user_profile.html', form=form, image_file=image_file)


#------------------VIEW BOOKING - FACILITY OWNER-------------

@app.route('/facility_owner/view_booking/<int:booking_id>')
@login_required
def view_booking_facility_owner(booking_id):
    '''Define the view function for the view booking page'''
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Booking not found.')
    check_in = booking.check_in.strftime('%B %d, %Y')
    check_out = booking.check_out.strftime('%B %d, %Y')
    created_at = booking.created_at.strftime('%B %d, %Y %I:%M %p')
    updated_at = booking.updated_at.strftime('%B %d, %Y %I:%M %p')
    return render_template('facility_owner/view_booking.html', booking=booking, check_in=check_in, check_out=check_out, created_at=created_at, updated_at=updated_at) 



#----------------ACCEPT BOOKING----------------

@app.route("/facility_owner/accept_booking/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def accept_booking(booking_id):
    """Define the view function for the accept booking page"""

    booking = Booking.query.get(booking_id)
    # print(booking)
    # print(booking.facility.owner_id)
    # print(current_user.id)


    # Check if the booking exists
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard_facility_owner'))
    
    # Assign the booking.facility.owner to the current_user

    # booking.facility.owner.email = current_user.email

    # Update booking status and commit to the database
    booking.updated_at = datetime.now()
    booking.status = 'accepted'
    db.session.commit()

    # Format the dates for the notification messages
    check_in = booking.check_in.strftime('%B %d, %Y')
    check_out = booking.check_out.strftime('%B %d, %Y')

    # Send notification to the user
    send_notification(
        booking.user.email,
        'Your Booking is Now Confirmed - Thank you!',
        template=(
            f'<p> Hi {booking.user.first_name}, </p>'
            f'<p> We are pleased to inform you that your booking at {booking.facility.name} '
            f'has been successfully accepted. </p>'
            f'<p> <b>Check-in:</b> {check_in} </p>'
            f'<p> <b>Check-out:</b> {check_out} </p>'
            f'<p> <b>Number of dogs:</b> {booking.number_of_dogs} </p>'
            f'<p> Thank you for using our services. We look forward to seeing you soon! </p>'
            f'<p> Best regards, </p> <p> The PawsitivelyBooked Team </p>'
        )
    )

    # Send notification to the facility owner
    send_notification(
        booking.facility.contact_email,
        f'New Booking Confirmed - Booking ID #{booking.id}',
        template=(
            f'<p> Hi {booking.facility.owner.first_name}, </p>'
            f'<p> You have accepted a booking for {booking.facility.name} with ID #{booking.id}. </p>'
            f'<p> <b>Check-in:</b> {check_in} </p>'
            f'<p> <b>Check-out:</b> {check_out} </p>'
            f'<p> <b>Number of dogs:</b> {booking.number_of_dogs} </p>'
            f'<p> Please check your dashboard for more details. </p>'
            f'<p> Best regards, </p> <p> The PawsitivelyBooked Team </p>'
        )
    )

    flash('Booking successfully accepted.', 'success')
    return redirect(url_for('dashboard_facility_owner'))



#---------------DECLINE BOOKING-------------------

@app.route("/facility_owner/decline_booking/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def decline_booking(booking_id):
    '''Define the view function for the decline booking page'''
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard_facility_owner'))
    
    booking.updated_at = datetime.now()
    booking.status = 'declined'
    db.session.commit()

    check_in = booking.check_in.strftime('%B %d, %Y')
    check_out = booking.check_out.strftime('%B %d, %Y')
    send_notification(booking.user.email,
                        'Your Booking Has Been Declined',
                        template=f'<p> Hi {booking.user.first_name}, </p> <p> We regret to inform you that your booking at {booking.facility.name} has been declined. </p> <p> Here are the details of your booking: </p> <p> <b>Check-in: </b> {check_in} </p> <p> <b>Check-out: </b> {check_out} </p> <p> <b>Number of dogs: </b>{booking.number_of_dogs} </p><p><b> Facility: </b>{booking.facility.name} </p> <p> We apologize for any inconvenience this may have caused. Please feel free to contact us for further assistance. </p> <p> Best regards, </p> <p> The PawsitivelyBooked Team </p>')
    flash('Booking successfully declined.', 'warning')
    return redirect(url_for('dashboard_facility_owner'))


#-----------------PRIVACY POLICY--------------------

@app.route('/privacy_policy')
def privacy_policy():
    '''Define the view function for the privacy policy page'''
    return render_template('privacy_policy.html')


#-----------------VIEW FACILITY - BY DOG OWNER---------------------

@app.route('/dog_owner/view_facility/<int:facility_id>')
@login_required
def view_facility(facility_id):
    '''Define the view function for the view facility page'''
    facility = Facility.query.get(facility_id)
    owner = User.query.get(facility.owner_id)
    if not facility:
        flash('Facility not found.', 'danger')
        return redirect(url_for('index'))
    facility_pictures = FacilityPhoto.query.filter_by(facility_id=facility_id).all()
    facility_pictures_path = [url_for('static', filename=f'images/facility_images/{photo.photo_path}') for photo in facility_pictures]
    return render_template('dog_owner/view_facility.html', facility=facility, owner=owner, facility_pictures_path=facility_pictures_path)



#------------------SET LOCATION--------------------

@app.route('/set_location', methods=['GET', 'POST'])
@login_required
def set_location():
    '''Define the view function for the set location page'''
    form = SetLocationForm()
    if form.validate_on_submit():
        street = form.street.data
        city = form.city.data
        postal_code = form.postal_code.data
        country = form.country.data

        location = f"{street}, {city}, {postal_code}, {country}"
        coordinates = get_location(location)

        if not coordinates:
            return redirect(url_for('set_location'))

        current_user.location = location
        current_user.latitude, current_user.longitude = coordinates
        db.session.commit()
        flash('Location successfully updated', 'success')
        return redirect(url_for('redirect_dashboard'))
    return render_template('dog_owner/location_form.html', form=form)

# --------------------LOGOUT--------------------

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
