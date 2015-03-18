#! /usr/bin/python

from twisted.python import log
import sys
import service
import webservice
import slave

if __name__ == '__main__':
    if len(sys.argv) > 1:
        log.startLogging(sys.stdout)
        opt = sys.argv[1].lower()
        if opt in ["rdebug", "debug", "start", "install", "remove", "stop", "restart", "status"]:

            service.main()

        elif sys.argv[1].lower() == "slave":

            username = sys.argv[2]
            user_dir = sys.argv[3]
            service_port = int(sys.argv[4])
            slave.main(username, user_dir, service_port)

        elif sys.argv[1].lower() == "justme":

            webservice.main(True)

    else:
        print "No command specified"
        print "Service args: debug, start, stop, restart, install, remove, status"
        print "or 'justme' for standalone"