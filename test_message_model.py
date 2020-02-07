"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

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


class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.commit()

        m1 = Message(
            text="test text for message",
            user_id=u1.id
        )

        db.session.add(m1)
        db.session.commit()

        self.u1 = User.query.get(u1.id)
        self.m1 = Message.query.get(m1.id)
        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        # User should have one message
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.m1.user_id, self.u1.id)
        self.assertEqual(f'{self.m1}', f"<Message #{self.m1.id}, User ID:{self.m1.user_id}, Text:{self.m1.text} @ {self.m1.timestamp}>")
