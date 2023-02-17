from sqlalchemy_utils import URLType
from climbunity_app.extensions import db
from climbunity_app.utils import FormEnum
from sqlalchemy.orm import backref
from flask_login import UserMixin
import enum

# class Category(FormEnum):
#     BOULDER = 1
#     SPORT = 2
#     TRAD = 3
#     TOPROPE = 4
#     INDOOR = 5
#     OUTDOOR = 6

# class Tag(FormEnum):
#     DYNAMIC = "Dynamic sections"
#     CRIMPY = "Crimp-focused"
#     SLOPER = "Slopers"
#     POCKET = "Pocket-pulling"
#     CRACK = "Crack"
#     OFFWIDTH = "Offwidth"
#     UNDERCLING = "Undercling"
#     FLAKE = "Prominent flake"
#     PINCH = "Pinchy"
#     HOOK = "Lots of heel/toe hooks"
#     ARETE = "Features an arête"
#     DIHEDRAL = "Features a dihedral"
#     SLAB = "Slabby"
#     VERTICAL = "Dead vertical"
#     STEEP = "Steeply overhung"
#     ROOF = "Features a roof section"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    has_gear = db.Column(db.Boolean, nullable=False)
    # climber_styles = db.relationship('Category', secondary='user_category')

    def __repr__(self):
        return f'<User: {self.username}>'

# climber_category_table = db.Table('user_category',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('category', db.Enum(Category))
# )

class Venue(db.Model):
    """Venue model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    open_hours = db.Column(db.Text(1000))
    description = db.Column(db.Text(1000))
    # venue_type = db.relationship('Category', secondary='venue_category')

    def __str__(self):
        return f'{self.title}'

    def __repr__(self):
        return f'{self.title}'

class Route(db.Model):
    """Route model"""
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    setter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    photo_url = db.Column(URLType)
    route_set_date = db.Column(db.Date)
    route_takedown_date = db.Column(db.Date)

    def __str__(self):
        return f'{self.title}'

    def __repr__(self):
        return f'{self.name}'

class Appointment(db.Model):
    """Appointment model"""
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    appointment_datetime = db.Column(db.DateTime, nullable=False)



# venue_category_table = db.Table('venue_category',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('category', db.Enum(Category))
# )
