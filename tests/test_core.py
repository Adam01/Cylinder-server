__author__ = 'Adam'

import unittest
import sys
import os
import subprocess
from time import sleep

sys.path.append(os.path.abspath("../Cylinder-server/"))

''' C.01 Have a test client able to connect to the server through SSL.
    Test is successful once the client connects, completes an SSL handshake,
    and is able to transmit data back and forth (using an echo server)

    Not sure how this can be tested internally...
'''


class C01TestSSLConnectivity(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0_ssl_connection(self):
        pass

    def test_1_ssl_data(self):
        pass


'''
    C.02 The system is able to authenticate supplied credentials on both Windows and Linux operating systems.
    The test will check the result of an authentication function, ensuring it returns null
    or throws an exception on failure and a class representing a login on success.
'''


@unittest.skipIf(os.environ.get('CI') is not None, "C.02 TestUserAuthentication: Cannot test user authentication on "
                                                   "Travis CI")
class C02TestUserAuthentication(unittest.TestCase):
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
        from authentication import Authentication, LoginError

        auth = Authentication(self.CORRECT_USERNAME, self.CORRECT_PASSWORD)

        self.assertIsInstance(auth, Authentication)
        self.assertEquals(auth.username, self.CORRECT_USERNAME)

        self.assertRaises(LoginError, Authentication, self.INCORRECT_USERNAME, self.INCORRECT_PASSWORD)

    @unittest.skipIf(sys.platform.startswith("win"), "C.02 test_user_authentication_pam: PAM not supported on windows")
    def test_user_authentication_pam(self):
        from authentication import Authentication, LoginError

        auth = Authentication(self.CORRECT_USERNAME, self.CORRECT_PASSWORD, True)

        self.assertIsInstance(auth, Authentication)
        self.assertEquals(auth.username, self.CORRECT_USERNAME)

        self.assertRaises(InvalidLogin, Authentication, self.INCORRECT_USERNAME, self.INCORRECT_PASSWORD, True)


'''
    C.03 The system is able to spawn a subprocess as another user.
    This may require the system to run a as a slightly elevated user.
    The test is successful once a process has been created and confirmed by outputting its current operating user.
'''


@unittest.skipIf(sys.platform.startswith("win"), "C.03 TestSpawnUserProcess: Requires to be run as a service "
                                                 "(or with abilities to impersonate, see CreateProcessAsUser)")
class C03TestSpawnUserProcess(unittest.TestCase):
    def setUp(self):
        from authentication import Authentication, LoginError

        self.auth = Authentication(C02TestUserAuthentication.CORRECT_USERNAME,
                                   C02TestUserAuthentication.CORRECT_PASSWORD)
        pass

    def tearDown(self):
        pass

    def test_create_process_as(self):
        from userprocess import create_process_as

        obj = create_process_as(self.auth, "whoami", stdout=subprocess.PIPE)
        obj.wait()
        out, err = obj.communicate()

        # Remove domain\\ and trailing \r\n
        out = out[out.find("\\") + 1:-2]

        self.assertEquals(out, C02TestUserAuthentication.CORRECT_USERNAME)

        pass