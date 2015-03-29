__author__ = 'Adam'
import sys
import os


def copy_some(obj_from, obj_to, names):
    for n in names:
        if hasattr(obj_from, n):
            v = getattr(obj_from, n)
            setattr(obj_to, n, v)


# Strip the advice and unchanged lines from a ndiff list
def make_comp_diff(delta_list):
    comp_delta = dict()
    i = 1
    for j, v in enumerate(delta_list):
        if v.startswith("  "):
            i += 1
        elif v.startswith("+ ") or v.startswith("- "):
            if i not in comp_delta:
                comp_delta[i] = list()
            comp_delta[i].append(v)
    return comp_delta


def get_exec_path():
    if sys.platform.startswith("win"):
        exeName = "Python.exe"
        import win32api
        # This usually points to PythonService.exe
        # Go hunting like winserviceutil does for that executable

        for path in [sys.prefix] + sys.path:
            look = os.path.join(path, exeName)
            if os.path.isfile(look):
                return win32api.GetFullPathName(look)
        # Try the global Path.
        try:
            return win32api.SearchPath(None, exeName)[0]
        except win32api.error:
            raise RuntimeError("Unable to locate python.exe")
    else:
        return sys.executable
