"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        testmessage = Message(text="test text for message",
                                   user_id=self.testuser.id)

        db.session.add(testmessage)
        db.session.commit()

        self.testmessage = Message.query.filter_by(text="test text for message").first()

    def test_add_message(self):
        """Can user add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            msg = Message.query.filter_by(text="Hello").first()

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello", html)

    def test_delete_message(self):
        """Can use delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f'/messages/{self.testmessage.id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            msg = Message.query.all()

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'@{self.testuser.username}', html)
            self.assertEqual(len(msg), 0)

    def test_logged_out_add_message(self):
        """Can't add message when logged out"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_logged_out_delete_message(self):
        """Can't delete message when logged out"""

        with self.client as c:
            resp = c.post(f"/messages/{self.testuser.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            
    def test_logged_out_follow_user(self):
        """Can't follow a user when logged out"""

        with self.client as c:
            resp = c.post(f"/users/follow/{self.testuser.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
    
    def test_add_message_different_user(self):
        """Can't add message when not the creator"""

        testuser2 = User.signup(username="testuser2",
                                    email="test2@test2.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()

        testmessage2 = Message(text="test message 2",
                               user_id=testuser2.id)
        db.session.add(testmessage2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg2 = Message.query.filter_by(text="test message 2").first()
            
            resp = c.post(f"/messages/{msg2.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    

        
