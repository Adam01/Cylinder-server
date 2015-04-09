__author__ = 'Adam'

import weakref
from functools import partial


class WeakMethodInvalid(Exception):
    def __str__(self):
        return "A weak method was invoked on a dead object"

class WeakCallable:
    def __init__(self, obj, func):
        self._obj = obj
        self._method = func

    def __call__(self, *args, **kws):
        return self._method(self._obj, *args, **kws)

    def __getattr__(self, attr):
        if attr == 'im_self':
            return self._obj
        if attr == 'im_func':
            return self._meth
        raise AttributeError(attr)

class WeakMethod:
    def __init__(self, fn):
        if hasattr(fn, "im_self"):
            self._obj = weakref.ref(fn.im_self)
            self._method = fn.im_func
        else:
            self._obj = None
            self._method = fn

    def get(self):
        if self._obj is None:
            return self._method
        elif self._obj() is not None:
            return WeakCallable(self._obj(), self._method)
        else:
            return None

    def dead(self):
        return self._obj is not None and self._obj() is None

    def __call__(self, *args, **kwargs):
        method = self.get()
        if method is None:
            raise WeakMethodInvalid()
        return method(*args, **kwargs)


class EventSubject:
    """
    Offers observer/subscriber pattern support
    """

    def __init__(self):
        self.subscribers = {}

    def cleanup(self, name=None):
        if name is None:
            i = 0
            for name in self.subscribers:
                i += self.cleanup(name)
            return i
        elif name in self.subscribers:
            to_remove = []
            for fn in self.subscribers[name]:
                if isinstance(fn, WeakMethod):
                    if fn.dead():
                        to_remove.append(fn)

            for fn in to_remove:
                self.subscribers[name].remove(fn)
                print "Removed ", fn
            return len(to_remove)
        else:
            return None

    def count(self, name):
        return 0 if self.cleanup(name) is None else len(self.subscribers[name])

    def subscribe(self, name, func):
        if not callable(func):
            raise TypeError("Expecting callable type")
        if name not in self.subscribers:
            self.subscribers[name] = []
        self.subscribers[name].append(WeakMethod(func))

    def notify(self, name, *args):
        i = 0
        if self.cleanup(name) is not None:
            for fn in self.subscribers[name]:
                fn(*args)
                i += 1
        return i


class EventRetainer(EventSubject):
    """
    Following class keeps hold of the event if a subscriber is not available.
    Re-fires as soon as a subscriber becomes available.
    """

    def __init__(self):
        EventSubject.__init__(self)
        self.retained = {}

    def subscribe(self, name, func):
        EventSubject.subscribe(self, name, func)
        if name in self.retained:
            for ev in self.retained[name]:
                EventSubject.notify(self, name, *ev)
            self.retained.pop(name, None)

    def notify(self, name, *args):
        n_called = EventSubject.notify(self, name, *args)
        if n_called == 0:
            if name not in self.retained:
                self.retained[name] = []
            self.retained[name].append(args)
        return n_called
