__author__ = 'Adam'


def copy_some(obj_from, obj_to, names):
    for n in names:
        if hasattr(obj_from, n):
            v = getattr(obj_from, n)
            setattr(obj_to, n, v)