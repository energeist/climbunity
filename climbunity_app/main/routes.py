import os
from os.path import exists
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from climbunity_app.utils import FormEnum
from climbunity_app.models import *
from climbunity_app.main.forms import *

from climbunity_app.extensions import app, db, bcrypt

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_venues = Venue.query.all()
    for venue in all_venues:
        print(venue.name)
    return render_template('home.html', all_venues=all_venues)

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

@main.route('/venue/<venue_id>', methods=['GET', 'POST'])
def venue_detail(venue_id):
    venue = Venue.query.get(venue_id)
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
    return render_template('venue_detail.html', form=form, venue=venue)

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

@main.route('/add_to_shopping_list/<item_id>', methods=['POST'])
@login_required
def add_to_shopping_list(item_id):
    item = GroceryItem.query.get(item_id)
    current_user.shopping_list_items.append(item)
    db.session.commit()
    flash(f"{item.name} added to cart")
    return redirect(url_for("main.shopping_list", item_id=item.id))

@main.route('/remove_from_shopping_list/<item_id>', methods=['POST'])
@login_required
def remove_from_shopping_list(item_id):
    item = GroceryItem.query.get(item_id)
    current_user.shopping_list_items.remove(item)
    db.session.commit()
    flash(f"{item.name} removed from cart")
    return redirect(url_for("main.shopping_list", item_id=item.id))

@main.route('/shopping_list')
@login_required
def shopping_list():
    shopping_list = current_user.shopping_list_items
    return render_template("shopping_list.html", shopping_list=shopping_list)