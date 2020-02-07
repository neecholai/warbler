"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from app import app
import os
from unittest import TestCase
from models import db, connect_db, bcrypt, User, Message, Follows
from sqlalchemy.exc import IntegrityError


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app
db.create_all()

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class UserModelTestCase(TestCase):
    """Test models for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Follows.query.delete()
        Message.query.delete()

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User.signup(username='username', email='email',
                         password='password', image_url=None)

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1 = User.query.filter(User.username == u1.username).first()
        self.u2 = User.query.filter(User.username == u2.username).first()
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(f'{self.u1}',
                         f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")

    def test_user_follows(self):
        """ Does following and getting followed by work?"""

        # Test if user1 is not following u2
        self.assertEqual(self.u1.is_following(self.u2), False)
        # Test if user 2 is not being followed by u1
        self.assertEqual(self.u1.is_followed_by(self.u2), False)

        self.u1.followers.append(self.u2)
        self.u1.following.append(self.u2)
        db.session.commit()

        # Test if user1 is following u2
        self.assertEqual(self.u1.is_following(self.u2), True)
        # Test if user 2 is not being followed by u1
        self.assertEqual(self.u1.is_followed_by(self.u2), True)

    def test_create_user_success(self):
        """ Is user successfully created? """

        is_password_hashed = bcrypt.check_password_hash(
            self.u2.password, 'password')

        self.assertEqual(self.u2.username, 'username')
        self.assertEqual(self.u2.email, 'email')
        self.assertTrue(is_password_hashed)
        self.assertEqual(len(User.query.all()), 2)

    def test_create_user_same_username(self):
        """" Is error created when creating user with username that already exists? """
        with self.assertRaises(IntegrityError):
            failed_user = User.signup(username=self.u1.username, email='email',
                                      password='password', image_url=None)
            db.session.add(failed_user)
            db.session.commit()

        db.session.remove()

    def test_create_user_same_email(self):
        """" Is error created when creating user with email that already exists? """

        with self.assertRaises(IntegrityError):
            failed_user = User.signup(username='failed_user', email=self.u1.email,
                                      password='password', image_url=None)
            db.session.add(failed_user)
            db.session.commit()

        db.session.remove()

    def test_create_user_no_entry(self):
        """" Is error created when creating user with invalid input? """

        with self.assertRaises(ValueError):
            failed_user = User.signup(username='failed_user', email='failed_email',
                                      password=None, image_url=None)
            db.session.add(failed_user)
            db.session.commit()

        db.session.remove()

    def test_authentication(self):

        user_success = User.authenticate(username=self.u2.username,
                                         password='password')
        user_fail = User.authenticate(username=self.u2.username,
                                      password='wrong_password')

        self.assertEqual(user_success, self.u2)
        self.assertFalse(user_fail)
