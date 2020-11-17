"""User model tests."""




import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows



os.environ['DATABASE_URL'] = "postgresql:///warbler-test"




from app import app



db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup('test1', 'dogs@dogs.com', 'testpassword', None)
        u1id = 1111
        u1.id = u1id

        u2 = User.signup('test2', 'cats@cats.com', 'testpassword', None)
        u2id = 2222
        u2.id = u2id

        db.session.commit()

        u1 = User.query.get(u1id)
        u2 = User.query.get(u2id)

        self.u1 = u1
        self.u1id = u1id

        self.u2 = u2
        self.u2id= u2id


        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()


        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)


        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))


    def test_valid_signup(self):
        u_test = User.signup('testing', 'tesing@testing.com', 'password', None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, 'testing')
        self.assertEqual(u_test.email, 'tesing@testing.com')
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith('$2b$'))


    def test_invalid_username_signup(self):
        invalid = User.signup(None, 'tesing@testing.com', 'password', None)
        uid = 99999
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_email_signup(self):
        invalid = User.signup('testing', None, 'password', None)
        uid = 99999
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)


    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "testpassword")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1id)


    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))


    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))