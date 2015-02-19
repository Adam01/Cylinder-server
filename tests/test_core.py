__author__ = 'Adam'

import unittest
import sys
import os
from time import sleep


''' Not sure how this can be tested internally... '''


class TestSSLConnectivity(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0_ssl_connection(self):
        pass

    def test_1_ssl_data(self):
        pass


'''The system is able to authenticate supplied credentials on both Windows and Linux operating systems.
The test will check the result of an authentication function, ensuring it returns null
or throws an exception on failure and a class representing a login on success.'''


@unittest.skipIf(os.environ.get('CI') is not None, "Cannot test user authentication on Travis CI")
class TestUserAuthentication(unittest.TestCase):
    CORRECT_USERNAME = "test"
    CORRECT_PASSWORD = "test"
    INCORRECT_USERNAME = "wrong"
    INCORRECT_PASSWORD = "wrong"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    ''' Test authentication class exists and is capable of constructing when valid credentials are supplied'''

    def test_user_authentication(self):
        import authentication

        auth = Authentication(self.CORRECT_USERNAME, self.CORRECT_PASSWORD)

        self.assertEquals(auth.username, self.CORRECT_USERNAME)

        self.assertRaises(InvalidLogin, Authentication, [self.INCORRECT_USERNAME, self.INCORRECT_PASSWORD])

    @unittest.skipIf(sys.platform.startswith("win"), "PAM not supported on windows")
    def test_user_authentication_pam(self):
        Authentication(self.CORRECT_USERNAME, self.CORRECT_PASSWORD, True)


'''The system is able to spawn a subprocess as another user.
This may require the system to run a as a slightly elevated user.
The test is successful once a process has been created and confirmed by outputting its current operating user.'''


class TestSpawnUserProcess(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_process_as(self):
        '''Create process'''
        sleep(5)
        '''Check files contents'''

        pass
