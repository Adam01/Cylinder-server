__author__ = 'Adam'

'''
Merge of basic.LineReceiver and cyclone.json-rpc
Also supports mapped arguments
'''

import types
from twisted.python import log


class JSONCallable:
    def __init__(self):
        self.current_id = 0
    def __call__(self, req):
        try:
            method = req["method"]
            params = req["params"]

            assert isinstance(method, types.StringTypes), "Invalid method type: %s" % type(method)
            function = getattr(self, "jsonrpc_%s" % method, None)

            if callable(function):
                if isinstance(params, types.DictType):
                    result = function(**params)
                elif isinstance(params, (types.ListType, types.TupleType)):
                    result = function(*params)
                else:
                    raise Exception("Invalid params type: %s" % type(params))
            else:
                raise AttributeError("method not found: %s" % method)
            error = None

        except Exception, e:
            log.msg("Bad Request: %s" % str(e))
            error = {'code': 0, 'message': str(e)}
            result = None
        data = {"result": result, "method": method, "error": error, "id": self.current_id}
        if "callback_id" in req:
            data["callback_id"] = req["callback_id"]
        self.current_id += 1
        return data