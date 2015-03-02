__author__ = 'Adam'

'''
Merge of basic.LineReceiver and cyclone.json-rpc
Also supports mapped arguments
'''

import types
from twisted.python import log


class JSONCallable:
    def __call__(self, req):
        jsonid = None
        try:
            jsonid = req["id"]
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
        return {"result": result, "error": error, "id": jsonid}
