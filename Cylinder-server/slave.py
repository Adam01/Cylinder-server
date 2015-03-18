__author__ = 'Adam'

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log
from twisted.protocols import basic
import json
import sys
from fsprocedures import FileSystemProcedures
import getpass
import os


class SlaveClient(basic.LineReceiver):
    def __init__(self):
        pass

    def connectionMade(self):
        log.msg("Made connection to server")
        msg = dict()
        msg["service_username"] = self.factory.username
        self.sendLine(json.dumps(msg))
        log.msg("Sent user identification")
        self.json_command_handler = FileSystemProcedures(self.factory.username, self.factory.user_dir)

    def dataReceived(self, sdata):
        data = json.loads(sdata)
        # handle cmd
        log.msg("Handling: %s" % sdata)
        # Once we've exhausted the prior options (server->slave commands)
        return_data = self.json_command_handler(data)
        return_str = json.dumps(return_data)
        log.msg("Responding: %s" % return_str)
        self.sendLine(return_str)

    def connectionLost(self, reason=protocol.connectionDone):
        log.msg("Lost connection to the server")


class SlaveFactory(protocol.ClientFactory):
    protocol = SlaveClient

    def clientConnectionFailed(self, connector, reason):
        log.msg("Connection failed, exiting")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        log.msg("Lost connection, exiting")
        reactor.stop()


def main(username, user_dir, service_port):
    log.startLogging(open('./log/slave_%s.out.txt' % username, 'w'))
    print username, user_dir, service_port
    f = SlaveFactory()
    f.username = username
    f.user_dir = user_dir

    os.environ["USERNAME"] = os.environ["USER"] = username
    os.environ["HOME"] = os.environ["USERPROFILE"] = user_dir

    reactor.connectTCP("localhost", service_port, f)
    reactor.run()
