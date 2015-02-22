__author__ = 'Adam'

import weakref

''' Credit to Joseph A. Knapka for the following two classes '''


class _weak_callable:
    def __init__(self, obj, func):
        self._obj = obj
        self._meth = func

    def __call__(self, *args, **kws):
        if self._obj is not None:
            return self._meth(self._obj * args, **kws)
        else:
            return self._meth(*args, **kws)

    def __getattr__(self, attr):
        if attr == 'im_self':
            return self._obj
        if attr == 'im_func':
            return self._meth
        raise AttributeError, attr


class WeakMethod:
    """ Wraps a function or, more importantly, a bound method, in
    a way that allows a bound method's object to be GC'd, while
    providing the same interface as a normal weak reference. """

    def __init__(self, fn):
        try:
            self._obj = weakref.ref(fn.im_self)
            self._meth = fn.im_func
        except AttributeError:
            # It's not a bound method.
            self._obj = None
            self._meth = fn

    def __call__(self):
        if self._dead():
            return None
        return _weak_callable(self._obj(), self._meth)

    def _dead(self):
        return self._obj is not None and self._obj() is None


''' Offers observer/subscriber pattern support '''


class EventSubject:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, name, func):
        if not callable(func):
            raise TypeError("Expecting callable type")
        if name not in self.subscribers:
            self.subscribers[name] = []
        self.subscribers[name].append(func)

    def subscribe_weak(self, name, func):
        self.subscribe(name, WeakMethod(func))

    def notify(self, name, *args):
        i = 0
        if name in self.subscribers:
            to_remove = []

            for fn in self.subscribers[name]:
                if isinstance(fn, WeakMethod):
                    if not fn._dead():
                        fn()(*args)
                        i += 1
                    else:
                        to_remove.append(fn)
                else:
                    fn(*args)
                    i += 1

            for fn in to_remove:
                self.subscribers[name].remove(fn)
                print "Removed ", fn
        return i


'''
    Following class keeps hold of the event if a subscriber is not available.
    Re-fires as soon as a subscriber becomes available.
'''


class EventRetainer(EventSubject):
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
        if EventSubject.notify(self, name, *args) == 0:
            if name not in self.retained:
                self.retained[name] = []
            self.retained[name].append(args)