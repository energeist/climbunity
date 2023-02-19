import os
from os.path import exists
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from climbunity_app.utils import FormEnum
from climbunity_app.models import *
from climbunity_app.main.forms import *
from climbunity_app.auth.forms import *

from climbunity_app.extensions import app, db, bcrypt

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

# homepage route 
@main.route('/')
def homepage():
    all_venues = Venue.query.all()
    for venue in all_venues:
        print(venue.name)
    return render_template('home.html', all_venues=all_venues)

######################
#  venue routes
######################

# create
@main.route('/new_venue', methods=['GET', 'POST'])
@login_required
def new_venue():
    form = VenueForm()
    if form.is_submitted():
        new_venue = Venue(
            name=form.name.data,
            address=form.address.data,
            open_hours=form.open_hours.data,
            description=form.description.data,
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('New venue was created successfully.')
        return redirect(url_for('main.venue_detail', venue_id=new_venue.id))
    return render_template('new_venue.html', form=form)

# read and update
@main.route('/venue/<venue_id>', methods=['GET', 'POST'])
def venue_detail(venue_id):
    venue = Venue.query.get(venue_id)
    routes = Route.query.filter_by(venue_id=venue_id).all()
    print(routes)
    form = VenueForm(obj=venue)

    if form.validate_on_submit():
        venue.name = form.venue.data
        venue.address = form.address.data
        venue.open_hours = form.open_hours.data
        venue.description = form.description.data
        db.session.commit()
        flash('Venue was edited successfully.')
        return redirect(url_for('main.venue_detail', venue_id=venue.id))

    venue = Venue.query.get(venue_id)
    return render_template('venue_detail.html', form=form, routes=routes, venue=venue)

######################
#  climbing route routes
######################

# create
@main.route('/new_route', methods=['GET', 'POST'])
@login_required
def new_route():
    form = RouteForm()
    if form.validate_on_submit():
        image_exists = os.path.exists(f'../static/img/{form.photo_url.data}')
        print(f"image exists: {image_exists}")
        if image_exists:
            image_url = form.photo_url.data
        else:
            image_url = '/static/img/no_image.jpeg'
        new_route = Route(
            name=form.name.data,
            venue_id = form.venue_id.data,
            setter_id = None,
            grade=form.grade.data,
            photo_url=image_url,
            route_set_date=form.route_set_date.data,
            route_takedown_date=form.route_takedown_date.data,
        )
        db.session.add(new_route)
        db.session.commit()
        flash('New item was created successfully.')
        return redirect(url_for('main.route_detail', route_id=new_route.id))
    return render_template('new_route.html', form=form)

# read and update
@main.route('/route/<route_id>', methods=['GET', 'POST'])
def route_detail(route_id):
    route = Route.query.get(route_id)
    form = RouteForm(obj=route)
    if form.validate_on_submit():
        image_exists = os.path.exists(f'/static/img/{form.photo_url.data}')
        print(f"image exists: {image_exists}")
        if image_exists:
            image_url = form.photo_url.data
        else:
            image_url = '/static/img/no_image.jpeg'
        route.name = form.name.data
        route.venue_id = form.venue_id.data
        route.grade = form.grade.data
        route.photo_url = image_url
        route.route_set_date = form.route_set_date.data
        route.route_takedown_date = form.route_takedown_date.data
        db.session.commit()
        flash('Route was edited successfully.')
        return redirect(url_for('main.route_detail', route_id=route.id))
    item = Route.query.get(route_id)
    return render_template('route_detail.html', form=form, route=route)

######################
#  project list routes
######################

# create
@main.route('/add_to_project_list/<route_id>', methods=['POST'])
@login_required
def add_to_project_list(route_id):
    route = Route.query.get(route_id)
    current_user.user_projects.append(route)
    db.session.commit()
    flash(f"{route.name} added to project list")
    return redirect(url_for("main.user_detail", user_id=current_user.id))

# update / delete
@main.route('/remove_from_project_list/<route_id>', methods=['POST'])
@login_required
def remove_from_project_list(route_id):
    route = Route.query.get(route_id)
    current_user.user_projects.remove(route)
    db.session.commit()
    flash(f"{route.name} removed from project list")
    return redirect(url_for("main.user_detail", user_id=current_user.id))

######################
#  ascent routes
######################

# create
@main.route('/log_ascent/<route_id>', methods=['POST'])
@login_required
def log_ascent(route_id):
    route = Route.query.get(route_id)
    form = AscentForm()
    if form.validate_on_submit():
        new_ascent = Ascent(
            user_id = current_user.id,
            route_id = route.id,
            send_date = form.ascent_date.data,
            send_type = form.ascent_type.data,
            send_rating = form.rating.data,
            send_comments = form.comments.data
        )
        db.session.add(new_ascent)
        db.session.commit()
        flash('New ascent was logged successfully.')
        return redirect(url_for('main.route_detail', route_id=route.id))
    return render_template('new_ascent.html', route_id=route.id, route=route, form=form)

# update

# delete
# @main.route('/remove_ascent/<route_id>', methods=['POST'])
# @login_required
# def remove_ascent(route_id):
#     route = Route.query.get(route_id)
#     current_user.user_projects.remove(route)
#     db.session.commit()
#     flash(f"{route.name} removed from project list")
#     return redirect(url_for("main.user_detail", user_id=current_user.id))

######################
#  profile routes
######################

# user creation route is in auth routes
# read and update
@main.route('/profile/<user_id>', methods=['GET', 'POST'])
def user_detail(user_id):
    user = User.query.get(user_id)
    if current_user.id == user.id:
        # form = SignUpForm(obj=user)
        # if form.validate_on_submit():
            # image_exists = os.path.exists(f'/static/img/{form.photo_url.data}')
            # print(f"image exists: {image_exists}")
            # if image_exists:
            #     image_url = form.photo_url.data
            # else:
            #     image_url = '/static/img/no_image.jpeg'
            # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # user.password=hashed_password
            # user.email = form.email.data
            # user.first_name = form.first_name.data
            # user.last_name = form.last_name.data
            # user.address = form.address.data
            # user.has_gear = form.has_gear.data
            # flash('User profile was edited successfully.')
        return render_template('user_detail.html', user=user)  
        # return redirect(url_for('main.user_detail', user_id=user.id))
    else:
        user = User.query.get(user_id)
        return render_template('user_detail.html', user=user)    

######################
#  appointment routes
######################

# create 
@main.route('/new_appointment', methods=['GET', 'POST'])
@login_required
def new_appointment():
    form = AppointmentForm()
    if form.validate_on_submit():
        new_appointment = Appointment(
            created_by=current_user,
            venue_id=1,
            appointment_date=form.appointment_date.data,
        )
        db.session.add(new_appointment)
        print(new_appointment.appointment_date)
        db.session.commit()
        flash('New appointment was created successfully.')
        return redirect(url_for('main.appointment_detail', appointment_id=new_appointment.id))
    else:
        new_appointment = Appointment(
            created_by=current_user,
            venue_id=1,
            appointment_date=form.appointment_date.data,
        )
        print("no validatorino")
        print(datetime.today())
    return render_template('new_appointment.html', form=form)

# @main.route('/appointment/<appointment_id>', methods=['GET', 'POST'])
# def appointment_detail(appointment_id):
#     appointment = Route.query.get(appointment_id)
#     form = AppointmentForm(obj=appointment)
#     if form.validate_on_submit():
#         appointment.appointment_date = form.appointment_date.data
#         db.session.commit()
#         flash('Route was edited successfully.')
#         return redirect(url_for('main.route_detail', route_id=route.id))
#     item = Route.query.get(route_id)
#     return render_template('route_detail.html', form=form, route=route)