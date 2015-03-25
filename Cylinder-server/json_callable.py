__author__ = 'Adam'

'''
Merge of basic.LineReceiver and cyclone.json-rpc
Also supports mapped arguments
'''
import types

import types
from twisted.python import log


class JSONCallableEscape:
    pass

class JSONCallable:
    def __init__(self):
        self.current_id = 0
        self.current_method = None
    def __call__(self, req):
        try:
            self.current_method = req["method"]
            params = req["params"]

            assert isinstance(self.current_method, types.StringTypes), "Invalid method type: %s" % type(
                self.current_method)
            function = getattr(self, "jsonrpc_%s" % self.current_method, None)

            if callable(function):
                if isinstance(params, types.DictType):
                    result = function(**params)
                elif isinstance(params, (types.ListType, types.TupleType)):
                    try:
                        result = function(*params)
                    except RuntimeError, e:
                        result = str(e)
                    except JSONCallableEscape, e:
                        result = e
                else:
                    raise TypeError("Invalid params type: %s" % type(params))
            else:
                raise AttributeError("method not found: %s" % self.current_method)
            error = None

        except (AttributeError, TypeError), e:
            log.msg("Bad Request: %s" % str(e))
            result = {"method": self.current_method, "id": self.current_id, "error": str(e)}

        if isinstance(result, types.StringTypes):
            data = result
        elif isinstance(result, types.BooleanType):
            data = {"method": self.current_method, "id": self.current_id, "result": result}
        elif isinstance(result, types.InstanceType):
            data = result.__dict__
        elif isinstance(result, types.DictType):
            data = result
        else:
            print "unhandled return type", type(result)
            data = {"method": self.current_method, "id": self.current_id}
        if "callback_id" in req:
            data["callback_id"] = req["callback_id"]
        self.current_id += 1
        return data