__author__ = 'Adam'

import cyclone.escape
import cyclone.web
import cyclone.websocket
import json
from twisted.python import log
from twisted.internet import reactor
from twisted.internet import ssl
import sys
import random
import string
import getpass

from authentication import Authentication, LoginError
from fsprocedures import FileSystemProcedures
from slaveservice import SlaveHandler
from json_callable import JSONCallable

import sockjs.cyclone


# Web/main server
class AnonymousCommands(JSONCallable):
    def __init__(self, handler):
        JSONCallable.__init__(self)
        self.handler = handler

    def jsonrpc_login(self, username, password):
        try:
            if self.handler.single_user and username != getpass.getuser():
                log.msg("Username does not match current user")
                return False
            self.handler.auth = Authentication(username, password)
            return True
        except LoginError:
            return False


class WSConnection(sockjs.cyclone.SockJSConnection):
    application = None

    def connectionMade(self, *args, **kwargs):
        self.auth = None
        self.single_user = (self.application.slave_handler is None)

    def connectionLost(self, reason=None):
        log.msg("ws closed")

    def messageReceived(self, message):
        log.msg("got message %s" % message)
        try:
            self.objectReceived(json.loads(message))
        except ValueError:
            pass

    def forwardToSlave(self, data):
        if self.application.slave_handler is not None:
            self.application.slave_handler.dispatch_command(self.auth, data)
        else:
            log.err("Slave processes not being used")

    def objectReceived(self, data):

        if self.auth is None:
            self.sendObject(AnonymousCommands(self)(data))

            if self.auth:
                if self.single_user:
                    self.fsprocs = FileSystemProcedures(self.auth.username, self.auth.home_dir)
                    self.fsprocs.subscribe("Tasks", self.sendObject)
                else:
                    self.application.slave_handler.subscribe_weak("out." + self.auth.username, self.sendObject)

        elif self.single_user:
            self.sendObject(self.fsprocs(data))
        else:
            self.forwardToSlave(data)


    def sendObject(self, obj):
        json_data = json.dumps(obj)
        log.msg("Sending back data to %s: %s" % (self.auth.username if self.auth else "Anonymous socket", json_data))
        self.sendMessage(json_data)


class MainHandler(cyclone.web.RequestHandler):
    def get(self):
        self.write("Hello, %s" % self.request.protocol)


def main(single_user=False, interface="127.0.0.1", key_file="config/server.key", cert_file="config/server.crt"):
    cookie_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(128))

    # Web handlers
    settings = dict(
        cookie_secret=cookie_secret,
        xsrf_cookies=True,
        autoescape=None,
    )

    SockJSRouter = sockjs.cyclone.SockJSRouter(WSConnection, '/ws')

    handlers = [
                   (r"/", MainHandler)
               ] + SockJSRouter.urls

    application = cyclone.web.Application(handlers, **settings)
    WSConnection.application = application
    application.slave_handler = None

    if not single_user:
        application.slave_handler = SlaveHandler()

    reactor.listenTCP(8888, application, interface=interface)
    reactor.listenSSL(8443, application, ssl.DefaultOpenSSLContextFactory(key_file, cert_file), interface=interface)

    # Disable signal handling on windows service
    use_sig_handlers = (single_user or sys.platform != "win32")

    reactor.run(installSignalHandlers=use_sig_handlers)
