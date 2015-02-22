__author__ = 'Adam'

import sys

'''
    Description:

        Use available methods to authenticate supplied system credentials.
        On windows the native LogonUser is used.
        On Linux, PAM is required and used by default.
        If specified, the passwd and shadow files are used - note this requires the calling user to be part of the
        shadow group.

    Usage:

        Authentication(username, password, use_PAM = True)


    Return:

        Authentication instance

        Authentication attributes:
            username
            [win32_token]

    Arguments:

        Username
        Password
        [use_PAM] - If False /etc/passwd and /etc/shadow are used

    Example:

        # Use PAM
        auth = Authentication("test","test")
        print "Authenticated %s" % auth.username

        # Use passwd and shadow
        # Calling process/user must be part of shadow group
        auth = Authentication("test","test",False)

    Throws:

        LoginError              -   Base of all exceptions

        Linux (for now):
        LoginNoPasswordError    -   No password has been set for the user
        LoginLockedError        -   User account has been locked
        LoginNoUser             -   No such user
        LoginExpiredError       -   The user account password has expired
        LoginInvalid            -   Invalid credentials supplied

'''


class LoginError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class LoginExpiredError(LoginError):
    def __init__(self, user):
        LoginError.__init__(self, "Password for user '%s' has expired" % user)


class LoginNoPasswordError(LoginError):
    def __init__(self, user):
        LoginError.__init__(self, "No password set for user '%s'" % user)


class LoginLockedError(LoginError):
    def __init__(self, user):
        LoginError.__init__(self, "Account for user '%s' is locked" % user)


class LoginNoUser(LoginError):
    def __init__(self, user):
        LoginError.__init__(self, "No such user '%s'" % user)


class LoginInvalid(LoginError):
    def __init__(self, user):
        LoginError.__init__(self, "Invalid login for '%s'" % user)


if sys.platform.startswith("win"):
    import win32security

    class Authentication:
        def __init__(self, username, password, unused=None):

            try:
                self.win32_token = win32security.LogonUser(username, None, password,
                                                           win32security.LOGON32_LOGON_INTERACTIVE,
                                                           win32security.LOGON32_PROVIDER_DEFAULT,
                )
            except win32security.error as e:

                # TODO throw appropriate error

                raise LoginError("Failed to log in as '%s': %s" % (username, e[2]))

            self.username = username
            self.home_dir = ""
            self.validated = True

elif sys.platform in ["linux2", "darwin"]:
    import crypt
    import pwd
    import spwd

    class Authentication:

        """
            Use PAM if the process's owner does not have access to /etc/shadow
            Access is usually with root or being a member of the shadow group
            Don't use root
        """

        def __init__(self, username, password, use_pam=True):
            try:

                pwd_entry = pwd.getpwnam(username)
                if use_pam:

                    import PAM

                    def pam_conv(_auth, _query_list, _userData):
                        return [(password, 0)]

                    try:
                        p = PAM.pam()
                        p.start("passwd")
                        p.set_item(PAM.PAM_USER, username)
                        p.set_item(PAM.PAM_CONV, pam_conv)
                        p.authenticate()
                        p.acct_mgmt()
                    except PAM.error, p_error:
                        print "Auth:", p_error
                        raise LoginInvalid(username)

                else:

                    enc_pw = pwd_entry[1]

                    if enc_pw in ["*", "x"]:
                        try:
                            shadow_entry = spwd.getspnam(username)
                            enc_pw = shadow_entry[1]
                            if enc_pw in ["NP", "!", "", None]:
                                raise LoginNoPasswordError(username)
                            elif enc_pw in ["LK", "*"]:
                                raise LoginLockedError(username)
                            elif enc_pw == "!!":
                                raise LoginNoPasswordError(username)
                        except KeyError:
                            raise LoginError("Unable to access shadow file")

                    if crypt.crypt(password, enc_pw) != enc_pw:
                        raise LoginInvalid(username)

                self.home_dir = pwd_entry[5]
            except KeyError, e:
                print "Auth:", str(e)
                raise LoginNoUser(username)

            self.username = username
            self.validated = True