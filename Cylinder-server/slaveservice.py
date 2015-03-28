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
from datetime import datetime


class SlaveConnectionHandler(basic.LineReceiver):
    def __init__(self):
        self.username = None

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

                if not self.factory.register_slave(self.username):
                    self.disconnect()
                else:
                    self.factory.subscribe_weak("in." + self.username, self.sendObject)
                    log.msg("%s's slave connected" % self.username)
            else:
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
        self.launching = []

    def register_slave(self, username):
        if username not in self.launching:
            log.err("Was not expecting a connection from %s's slave" % username)
        elif self.count("in." + username):
            log.err("There is already an active slave connection for %s" % username)
        else:
            self.launching.remove(username)
            return True
        return False

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

        self.launching.append(user_auth.username)

    def dispatch_command(self, user_auth, cmd_obj):
        if self.notify("in." + user_auth.username, cmd_obj) == 0 and user_auth.username not in self.launching:
            self.launch_slave_process(user_auth)
