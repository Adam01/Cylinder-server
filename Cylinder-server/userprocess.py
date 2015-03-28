__author__ = 'Adam'

import sys
import subprocess

'''
    Description:

        Create a process as another user.
        Basically popen with a prefixed authentication parameter.

        On windows this requires the calling process/user to have impersonate, create objects, and change process token
        privileges (AKA Local Service user)
        On Linux sudo is used requiring the user has the correct permissions in the sudoers file.


    Usage:

        create_process_as( Authentication, args, **kwargs)


    Return:

        Result of subprocess.popen


    Arguments:

        Authentication instance with valid username credential (windows requires the win32_token attribute to be set)
        List/String of arguments forwarded to popen
        dict of args also forwarded to popen


    Example:

        auth = Authentication("test","test")
        popen_obj = create_process_as(auth, "whoami")
        popen_obj.wait()
        # etc...

    Note: I can't seem to get popen's env argument working with this
'''

if sys.platform.startswith("win"):
    import win32process
    import useful

    def __convert_startup_info(old_info):
        new_info = None
        if old_info.__class__ is subprocess.STARTUPINFO:
            new_info = win32process.STARTUPINFO()
        elif type(old_info) is type(win32process.STARTUPINFO()):
            new_info = subprocess.STARTUPINFO()
        useful.copy_some(old_info, new_info, ["dwFlags", "hStdInput", "hStdOutput", "hStdErr", "wShowWindow"])
        return new_info

    ''' Replace builtin CreateProcess and call CreateProcessAsUser if a token is supplied '''

    __builtin_CreateProcess = subprocess._subprocess.CreateProcess

    def __create_process(*args):
        if hasattr(args[8], "token"):
            arg_list = list(args)
            arg_list[8] = __convert_startup_info(arg_list[8])
            return win32process.CreateProcessAsUser(args[8].token, *tuple(arg_list))
        else:
            return __builtin_CreateProcess(*args)

    subprocess._subprocess.CreateProcess = __create_process

    def create_process_as(user_auth, args=list(), **kwargs):
        if isinstance(args, str):
            args = list(args)
        if "startupinfo" not in kwargs:
            kwargs["startupinfo"] = subprocess.STARTUPINFO()
        kwargs["startupinfo"].token = user_auth.win32_token
        return subprocess.Popen(args, **kwargs)

elif sys.platform in ["linux2", "darwin"]:
    import subprocess

    def create_process_as(user_auth, args=list(), **kwargs):
        if isinstance(args, str):
            args = list(args)
        return subprocess.Popen(["sudo", "-nu", user_auth.username] + args, **kwargs)
