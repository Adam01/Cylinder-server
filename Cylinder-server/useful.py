__author__ = 'Adam'


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
            if not comp_delta.has_key(i):
                comp_delta[i] = list()
            comp_delta[i].append(v)
    return comp_delta

