__author__ = 'Adam'

import unittest
import os
import sys
from authentication import Authentication, LoginInvalid


@unittest.skipIf(os.environ.get('CI') is not None, "Cannot test user authentication on Travis CI")
class TestAuthenticationClass(unittest.TestCase):
    CORRECT_USERNAME = "test"
    CORRECT_PASSWORD = "test"
    INCORRECT_USERNAME = "wrong"
    INCORRECT_PASSWORD = "wrong"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_construct(self):
        from authentication import Authentication, LoginError

        # Invalid number of args
        self.assertRaises(TypeError, Authentication)
        self.assertRaises(TypeError, Authentication, self.CORRECT_USERNAME)

        # Correct usage, invalid credentials
        self.assertRaises(LoginError, Authentication, self.INCORRECT_USERNAME, self.INCORRECT_PASSWORD)

        # Correct usage
        auth = Authentication(self.CORRECT_USERNAME, self.CORRECT_PASSWORD)

        self.assertIsInstance(auth, Authentication)
        self.assertIsNotNone(auth.username)
        self.assertEquals(auth.username, self.CORRECT_USERNAME)
        if sys.platform.startswith("win"):
            self.assertIsNotNone(auth.win32_token)
            self.assertEquals(auth.win32_token.__class__.__name__, "PyHANDLE")

