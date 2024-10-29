'''Create a Flask application instance'''

import os
from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import geopy
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler



app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'testing':
    app.config.from_object('config.TestConfig')
else:
    app.config.from_object(Config)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'warning'
geolocator = geopy.Nominatim(user_agent="app")
mail = Mail(app)
scheduler = APScheduler()
scheduler.init_app(app)




from app import routes, models