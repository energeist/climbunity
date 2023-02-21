from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FloatField, PasswordField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, URL, ValidationError, email_validator, email
from climbunity_app.utils import FormEnum
from climbunity_app.models import *
from climbunity_app.extensions import app, db, bcrypt
from wtforms.fields.html5 import DateField


class SignUpForm(FlaskForm):
    username = StringField(
        'User Name',
        validators=[DataRequired(), Length(min=3, max=50)]
        )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)]
        )
    email = StringField(
        'Email', 
        validators=[DataRequired(message="You must input a valid email address.")]
        )
    first_name = StringField(
        'First Name',
        validators=[DataRequired(message="Your must enter your first name.")]
    )
    last_name = StringField('Last Name')
    address = StringField(
        'Address', 
        validators=[DataRequired("You must enter your address.")]
    )
    climber_styles = QuerySelectMultipleField('Select your climbing styles',
        query_factory=lambda: Style.query
    )
    has_gear = BooleanField('Have your own gear?', default="unchecked")
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        existing_email = User.query.filter_by(email=email.data).first()
        if existing_email:
            raise ValidationError('That email address is already associated with an account. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('User Name',
        validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('No user with that username. Please try again.')

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not bcrypt.check_password_hash(
                user.password, password.data):
            raise ValidationError('Password doesn\'t match. Please try again.')
