import daemon
import os
from twisted.python import log
import webservice
import sys


class ServiceClass(daemon.Daemon):
    def __init__(self):
        daemon.Daemon.__init__(self, './pidfile', stdin='/dev/null',
                               stdout='./service.out.txt',
                               stderr='./service.out.txt')

    def run(self):
        log.startLogging(sys.stdout)
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        webservice.main()


def main():
    argv = sys.argv

    if len(argv) <= 1:
        try:
            fname = os.path.split(sys.argv[0])[1]
        except Exception:
            fname = sys.argv[0]

        print "Usage: '%s [options] start|stop|restart'" % fname

    cmd = argv[1].lower()
    svc = ServiceClass()

    if cmd == "start":
        svc.start()
    elif cmd == "stop":
        svc.run()
    elif cmd == "restart":
        svc.restart()
