from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FloatField, PasswordField, IntegerField, RadioField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, URL, ValidationError, NumberRange
from climbunity_app.utils import FormEnum
from climbunity_app.models import *
from climbunity_app.extensions import app, db, bcrypt
from wtforms.fields.html5 import DateField, TimeField, DateTimeField, DateTimeLocalField
# from flask_login import current_user

class VenueForm(FlaskForm):
    """Form for adding/updating a Venue."""
    name = StringField('Venue Name',
    validators=[
        DataRequired(), 
        Length(min=3, max=80, message="Your venue name needs to be betweeen 3 and 80 chars")
    ])
    address = StringField('Address',
    validators=[
        DataRequired(), 
        Length(min=3, max=80, message="Your need to enter a street address or general location")
    ])
    open_hours = StringField('Hours of Operation')
    description = StringField('Description')
    submit = SubmitField('Submit')

class RouteForm(FlaskForm):
    """Form for adding/updating a Route."""

    name = StringField('Route Name', 
        validators=[
            DataRequired(), 
            Length(min=1, max=200, message="Your route name needs to be betweeen 1 and 200 chars")
        ])
    venue_id = IntegerField('Gym / Crag') ## change this to a select field with queryfactory for venues
    grade = StringField('Route Grade')
    photo_url = StringField('Photo URL')
    route_set_date = DateField('Route Set Date')
    route_takedown_date = DateField('Projected Route Takedown Date')
    submit = SubmitField('Submit')

class AscentForm(FlaskForm):
    """Form for logging a route ascent"""
    ascent_date = DateField("Date of ascent", validators=[DataRequired()])
    ascent_type = SelectField("Type of ascent", choices=SendType.choices(), validators=[DataRequired()])
    rating = RadioField("Personal route rating", choices=[0,1,2,3,4,5])
    comments = StringField("Comments", validators=[Length(max=1000, message="Please limit comments to 1000 characters.")])
    submit = SubmitField('Submit')

class AppointmentForm(FlaskForm):
    """Form for creating an appointment"""
    appointment_date = DateField(
        'Appointment Date and Time',
    )
    def validate_datetime(self, appointment_date):
        print("thing")
        # print(datetime.now())
        # if appointment_datetime.data < datetime.now():
        #     raise ValidationError("The appointment cannot be in the past!")
        appointment_date = DateField(
        'Appointment Date',
        validators=[DataRequired()])
    # appointment_time = TimeField('Appointment Time')
    submit = SubmitField('Submit')
