__author__ = 'Adam'

import unittest
import sys
import os
import subprocess

# Just make sure /Cylinder-server is appended to the path beforehand
#sys.path.append(os.path.abspath("../Cylinder-server/"))

''' C.01 Have a test client able to connect to the server through SSL.
    Test is successful once the client connects, completes an SSL handshake,
    and is able to transmit data back and forth (using an echo server)

    Not sure how this can be tested internally...


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


'''
    C.02 The system is able to authenticate supplied credentials on both Windows and Linux operating systems.
    The test will check the result of an authentication function, ensuring it returns null
    or throws an exception on failure and a class representing a login on success.
'''


# @unittest.skipIf(os.environ.get('CI') is not None, "C.02 TestUserAuthentication: Cannot test user authentication on "
#"Travis CI")
@unittest.skipIf(os.environ.get("TEST_USER") is None or
                 os.environ.get("TEST_PASSWORD") is None,
                 "TestUserAuthentication: No correct test user supplied")
class C02TestUserAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.correct_username = os.environ.get("TEST_USER")
        cls.correct_password = os.environ.get("TEST_PASSWORD")
        cls.incorrect_username = "nonexistantuser"
        cls.incorrect_password = "wrong"

    def tearDown(self):
        pass

    ''' Test authentication class exists and is capable of constructing when valid credentials are supplied'''

    def test_user_authentication(self):
        from authentication import Authentication, LoginError

        auth = Authentication(self.correct_username, self.correct_password, False)

        self.assertIsInstance(auth, Authentication)
        self.assertEquals(auth.username, self.correct_username)

        self.assertRaises(LoginError, Authentication, self.incorrect_username, self.incorrect_password)

    @unittest.skipIf(sys.platform.startswith("win"), "C.02 test_user_authentication_pam: PAM not supported on windows")
    def test_user_authentication_pam(self):
        from authentication import Authentication, LoginError

        auth = Authentication(self.correct_username, self.correct_password, True)

        self.assertIsInstance(auth, Authentication)
        self.assertEquals(auth.username, self.correct_username)

        self.assertRaises(LoginError, Authentication, self.incorrect_username, self.incorrect_password, True)


'''
    C.03 The system is able to spawn a subprocess as another user.
    This may require the system to run a as a slightly elevated user.
    The test is successful once a process has been created and confirmed by outputting its current operating user.
'''


@unittest.skipIf(os.environ.get("TEST_USER") is None or
                 os.environ.get("TEST_PASSWORD") is None or
                 sys.platform.startswith("win"),
                 "TestSpawnUserProcess: No correct test user supplied || Needs windows service user")
class C03TestSpawnUserProcess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.correct_username = os.environ.get("TEST_USER")
        cls.correct_password = os.environ.get("TEST_PASSWORD")

        from authentication import Authentication

        cls.auth = Authentication(cls.correct_username, cls.correct_password)


    def tearDown(self):
        pass

    def test_create_process_as(self):
        from userprocess import create_process_as

        obj = create_process_as(self.auth, "whoami", stdout=subprocess.PIPE)
        obj.wait()
        out, err = obj.communicate()

        if sys.platform.startswith("win"):
            # Remove domain\\
            out = out[out.find("\\") + 1:]
            # Remove trailing \r\n
            out = out[:-2]
        else:
            print out
            out = out[:-2]

        self.assertEquals(out, self.correct_username)

        pass
