import functools

__author__ = 'Adam'

"""
Merge of basic.LineReceiver and cyclone.json-rpc
Also supports mapped arguments
"""

import types


class JSONError(Exception):
    def __init__(self, err):
        self.error = err
        pass

    def __str__(self):
        return self.error

class JSONCallable:
    def __init__(self):
        self.current_id = 0
        self.current_method = None
        self.current_input = None
        self.current_params = None
        self.current_result = None
        self.current_exception = None

    def on_exception(self, e):
        return str(e)

    def post_process(self):
        return

    def __call__(self, req):
        try:
            self.current_exception = None
            self.current_result = None

            self.current_input = req
            self.current_method = self.current_input["method"]
            self.current_params = self.current_input["params"]

            if not isinstance(self.current_method, types.StringTypes):
                raise TypeError("Invalid method type: {}".format(
                    self.current_method
                ))

            function = getattr(self, "jsonrpc_%s" % self.current_method, None)

            if callable(function):
                if isinstance(self.current_params, types.DictType):
                    function = functools.partial(function, **self.current_params)
                elif isinstance(self.current_params, (types.ListType, types.TupleType)):
                    function = functools.partial(function, *self.current_params)
                else:
                    raise TypeError("Invalid params type: %s" % type(self.current_params))
            else:
                raise AttributeError(
                    "method not found: %s" % self.current_method)
        except (TypeError, AttributeError), e:
            raise JSONError(str(e))

        try:
            self.current_result = function()
        except Exception, e:
            self.current_exception = e
            if not self.on_exception():
                raise

        self.post_process()

        self.current_id += 1
        return self.current_result
