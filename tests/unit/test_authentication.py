__author__ = 'Adam'

import unittest
import os
import sys
from authentication import Authentication, LoginInvalid


# @unittest.skipIf(os.environ.get('CI') is not None,
# "Cannot test user authentication on Travis CI")
@unittest.skipIf(os.environ.get("TEST_USER") is None or
                 os.environ.get("TEST_PASSWORD") is None,
                 "TestUserAuthentication: No correct test user supplied")
class TestAuthenticationClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.correct_username = os.environ.get("TEST_USER")
        cls.correct_password = os.environ.get("TEST_PASSWORD")
        cls.incorrect_username = "nonexistantuser"
        cls.incorrect_password = "wrong"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_construct(self):
        # Invalid number of args
        self.assertRaises(TypeError, Authentication)
        self.assertRaises(TypeError, Authentication, self.correct_username)

        # Correct usage, invalid credentials
        self.assertRaises(LoginInvalid, Authentication,
                          self.incorrect_username, self.incorrect_password)

        # Correct usage
        auth = Authentication(self.correct_username, self.correct_password)

        self.assertIsInstance(auth, Authentication)
        self.assertIsNotNone(auth.username)
        self.assertEquals(auth.username, self.correct_username)

        self.assertTrue(auth.validated)

        if sys.platform.startswith("win"):
            self.assertIsNotNone(auth.win32_token)
            self.assertEquals(auth.win32_token.__class__.__name__, "PyHANDLE")
