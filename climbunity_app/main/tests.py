import os
import unittest
import app

from datetime import date, datetime
from climbunity_app.extensions import app, db, bcrypt
from climbunity_app.models import *

"""
Run these tests with the command:
python -m unittest climbunity_app.main.tests
^^^ might not work, use
python3 -m unittest discover instead (or this might just register zero tests because why not lol)
"""

#################################################
# Setup
#################################################

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_user():
    password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
    user = User(
        username='me1',
        password=password_hash,
        email='test123@test.com',
        first_name='Test',
        last_name='User',
        address='123 Test. St',
        has_gear=True
        )
    db.session.add(user)
    db.session.commit()

def create_venue():
    v1 = Venue(
        name = "Rock Oasis",
        address = "Dundas and Carlaw"
    )
    db.session.add(v1)
    db.session.commit()

def create_route():
    venue = Venue.query.first()
    user = User.query.first()
    r1 = Route(
        venue_id = 1,
        setter_id = 1,
        name = "Silence",
        grade = "9c+",
    )
    db.session.add(r1)
    db.session.commit()
    # route = Route.query.first()
    # print(route)

def create_ascent():
    user = User.query.first()
    route = Route.query.first()
    a1 = Ascent(
        user_id = user,
        route_id = route
    )
    db.session.add(a1)
    db.session.commit()

def create_appointment():
    user = User.query.first()
    venue = Venue.query.first()
    apt1 = Appointment(
        created_by = user,
        venue_id = venue,
        appointment_datetime = datetime.now()
    )
    db.session.add(apt1)
    db.session.commit()

#################################################
# Tests
#################################################

class MainTests(unittest.TestCase):
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
 
    def test_homepage_logged_out(self):
        """Test that the venues show up on the homepage."""
        # Set up
        create_user()
        create_venue()

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Rock Oasis', response_text)
        self.assertIn('Users', response_text)
        self.assertIn('Dundas and Carlaw', response_text)
        self.assertIn('Log In', response_text)
        self.assertIn('Sign Up', response_text)

        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged in users)
        self.assertNotIn('New Venue', response_text)
        self.assertNotIn('New Route', response_text)
        self.assertNotIn('New Appointment', response_text)
 
    def test_homepage_logged_in(self):
        """Test that the venue show up on the homepage."""
        # Set up
        create_user()
        create_venue()
        login(self.app, 'me1', 'password123')

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Rock Oasis', response_text)
        self.assertIn('Users', response_text)
        self.assertIn('Dundas and Carlaw', response_text)
        self.assertIn('New Venue', response_text)
        self.assertIn('New Route', response_text)
        self.assertIn('New Appointment', response_text)
 
        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged out users)
        self.assertNotIn('Log In', response_text)
        self.assertNotIn('Sign Up', response_text)

    def test_venue_detail_logged_out(self):
        """Test that the book appears on its detail page."""
        # Set up
        create_user()
        create_venue()
        create_route()

        response = self.app.get('/venue/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        
        # print(response_text)
        self.assertIn("<h1>Venue - Rock Oasis</h1>", response_text)
        self.assertIn("<p><strong>Address / Location:</strong> Dundas and Carlaw</p>", response_text)
        self.assertIn("<p><strong>Silence</strong></p></a>", response_text)

        self.assertNotIn("Project Route!", response_text)
        self.assertNotIn("Log an ascent!", response_text)
        self.assertNotIn("Delete route", response_text)

    def test_venue_detail_logged_in(self):
        """Test that the venue appears on its detail page."""
        create_user()
        login(self.app, 'me1', 'password123')  
        create_venue()
        create_route()

        response = self.app.get('/venue/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        
        # print(response_text)
        self.assertIn("<h1>Venue - Rock Oasis</h1>", response_text)
        self.assertIn("<p><strong>Address / Location:</strong> Dundas and Carlaw</p>", response_text)
        self.assertIn("<p><strong>Silence</strong></p></a>", response_text)
        self.assertIn('<input type="submit" value="Project route!">', response_text)
        self.assertIn('<input type="submit" value="Log an ascent!">', response_text)
        self.assertIn('<form method="POST" action="/delete_route/1">', response_text)
        self.assertIn("<legend>Edit this climbing venue:</legend>", response_text)

    def test_create_venue(self):
        """Test creating a venue."""
        # Set up
        create_user()
        login(self.app, 'me1', 'password123')

        # Make POST request with data
        post_data = {
            'name':'Gravity',
            'address':'Frid St. Hamilton',
        }
        self.app.post('/new_venue', data=post_data)

        # Make sure venue was created as we'd expect
        created_venue = Venue.query.filter_by(name='Gravity').one()
        self.assertIsNotNone(created_venue)
        self.assertEqual(created_venue.address, 'Frid St. Hamilton')

    def test_update_venue(self):
    #     """Test updating a venue."""
        create_user()
        login(self.app, 'me1', 'password123')  
        create_venue()
        create_route()

        response = self.app.get('/venue/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        venue = Venue.query.get(1)
        # Make POST request with data
        post_data = {
            'name':"Rock Oasis",
            'address':"Carlaw and Dundas",
            'open_hours':"9-9 every day",
            'description':"an indoor gym with routes"
        }
        self.app.post('/venue/1', data=post_data)
        
        # Make sure the venue was updated as we'd expect
        venue = Venue.query.get(1)
        self.assertEqual(venue.address, "Carlaw and Dundas")
        self.assertEqual(venue.open_hours, "9-9 every day")
        self.assertEqual(venue.description, "an indoor gym with routes")

    def test_create_route(self):
        """Test creating a book."""
        # Set up
        create_user()
        create_venue()
        login(self.app, 'me1', 'password123')

        # Make POST request with data
        post_data = {
            'venue_id':1,
            'setter_id':1,
            'name':"Return of the Sleepwalker",
            'grade':"V17"
        }
        self.app.post('/new_route', data=post_data, follow_redirects=True)

        # Make sure the route was created properly
        created_route = Route.query.one()
        self.assertIsNotNone(created_route)
        self.assertEqual(created_route.grade, 'V17')

    def test_update_route(self):
    #     """Test updating a route."""
        create_user()
        login(self.app, 'me1', 'password123')  
        create_venue()
        create_route()

        response = self.app.get('/route/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        route = Route.query.get(1)
        # Make POST request with data
        post_data = {
            'venue_id':1,
            'setter_id':1,
            'name':"Sleepwalker",
            'grade':"V16",
        }
        response = self.app.post('/route/1', data=post_data, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        # print(response_text)
        # Make sure the route was updated as we'd expect
        route = Route.query.get(1)
        self.assertEqual(route.name, "Sleepwalker")
        self.assertEqual(route.grade, "V16")

    # def test_create_book_logged_out(self):
    #     """
    #     Test that the user is redirected when trying to access the create book 
    #     route if not logged in.
    #     """
    #     # Set up
    #     create_books()
    #     create_user()

    #     # Make GET request
    #     response = self.app.get('/create_book')

    #     # Make sure that the user was redirecte to the login page
    #     self.assertEqual(response.status_code, 302)
    #     self.assertIn('/login?next=%2Fcreate_book', response.location)

    # def test_create_author(self):
    #     """Test creating an author."""
    #     # TODO: Create a user & login (so that the user can access the route)
    #     create_user()
    #     login(self.app, 'me1', 'password')

    #     # TODO: Make a POST request to the /create_author route
    #     post_data = {
    #         'name': 'David Eddings',
    #         'biography': 'Guy who writes good fantasy novels'
    #     }
    #     self.app.post('/create_author', data=post_data)

    #     # TODO: Verify that the author was updated in the database
    #     created_author = Author.query.filter_by(name='David Eddings').one()
    #     self.assertIsNotNone(created_author)
    #     self.assertEqual(created_author.name, 'David Eddings')

    # def test_create_genre(self):
    #     # TODO: Create a user & login (so that the user can access the route)
    #     create_user()
    #     login(self.app, 'me1', 'password')

    #     # TODO: Make a POST request to the /create_genre route,
    #     post_data = {
    #         'name': 'Fantasy',
    #     }
    #     self.app.post('/create_genre', data=post_data) 

    #     # TODO: Verify that the genre was updated in the database
    #     created_genre = Genre.query.filter_by(name='Fantasy').one()
    #     self.assertIsNotNone(created_genre)
    #     self.assertEqual(created_genre.name, 'Fantasy')

    # def test_profile_page(self):
    #     # TODO: Make a GET request to the /profile/me1 route
    #     create_user()
    #     response = self.app.get('/profile/me1', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)

    #     # TODO: Verify that the response shows the appropriate user info
    #     response_text = response.get_data(as_text=True)
    #     self.assertIn("Welcome to me1's profile", response_text)

    # def test_favorite_book(self):
    #     # TODO: Login as the user me1
    #     create_books()
    #     create_user()
    #     login(self.app, 'me1', 'password')

    #     # TODO: Make a POST request to the /favorite/1 route

    #     self.app.post('/favorite/1')

    #     # TODO: Verify that the book with id 1 was added to the user's favorites
    #     user = User.query.filter_by(id=1).one()
    #     self.assertIn("Mockingbird", user.favorite_books[0].title)

    # def test_unfavorite_book(self):
    #     # TODO: Login as the user me1, and add book with id 1 to me1's favorites
    #     create_books()
    #     create_user()
    #     login(self.app, 'me1', 'password')
    #     self.app.post('/favorite/1')
    #     user = User.query.filter_by(id=1).one()
    #     self.assertIn("Mockingbird", user.favorite_books[0].title)

    #     # TODO: Make a POST request to the /unfavorite/1 route
    #     self.app.post('/unfavorite/1')
    #     user = User.query.filter_by(id=1).one()
    #     self.assertEqual([], user.favorite_books)
    #     # TODO: Verify that the book with id 1 was removed from the user's 
    #     # favorites

