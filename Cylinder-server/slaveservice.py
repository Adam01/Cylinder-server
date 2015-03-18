__author__ = 'Adam'

from twisted.protocols import basic
from twisted.internet import protocol
from twisted.python import log
from twisted.internet import reactor
import userprocess
import subject
import json
import os
import useful


class SlaveConnectionHandler(basic.LineReceiver):
    def __init__(self):
        self.username = None

    def rawDataReceived(self, data):
        pass

    def connectionMade(self):
        log.msg("Connected to a slave")

    def connectionLost(self, reason=protocol.connectionDone):

        if self.username is not None:
            log.msg("Lost connection to %s's slave" % self.username)
        else:
            log.msg("Lost connection to unknown slave")

    def disconnect(self):
        log.err("Disconnecting %s's slave connection" % (self.username or "UNKNOWN"))
        self.transport.loseConnection()

    def lineReceived(self, message):
        try:
            self.objectReceived(json.loads(message))
        except ValueError:
            log.err("Received non-JSON data on service connection")
            self.disconnect()

    def objectReceived(self, data):
        if self.username is None:
            if "service_username" in data:
                self.username = data["service_username"]
                self.factory.subscribe_weak("in." + self.username, self.sendObject)
                log.msg("%s's slave connected" % self.username)
            else:
                # This took so long to find
                self.disconnect()
        else:
            log.msg("Notifying handlers from %s's slave" % self.username)
            self.factory.notify("out." + self.username, data)

    def sendObject(self, obj):
        json_data = json.dumps(obj)
        log.msg("Forwarding data to %s's slave: %s" % (self.username, json_data))
        self.sendLine(json_data)


class SlaveHandler(protocol.ServerFactory, subject.EventRetainer):
    def __init__(self):
        subject.EventRetainer.__init__(self)
        self.protocol = SlaveConnectionHandler
        listener = reactor.listenTCP(0, self)
        self.service_port = listener.getHost().port
        self.exec_path = useful.get_exec_path()
        self.script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

    def launch_slave_process(self, user_auth):
        log.msg("Launching %s %s %s %s %s"
                % (self.exec_path, self.script_path, "slave", user_auth.home_dir, self.service_port)
        )

        userprocess.create_process_as(user_auth, [
            self.exec_path,
            self.script_path,
            "slave",
            user_auth.username,
            user_auth.home_dir,
            str(self.service_port)
        ])

    def dispatch_command(self, user_auth, cmd_obj):
        if self.notify("in." + user_auth.username, cmd_obj) == 0:
            # There wasn't a subscribed handler
            self.launch_slave_process(user_auth)
