__author__ = 'Adam'

from twisted.internet import reactor
from twisted.python import log

import win32serviceutil
import win32service
import os
import sys


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "FileService"
    _svc_display_name_ = "File Service"


    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        reactor.stop()

    def SvcDoRun(self):

        self.debug = ("debug" in sys.argv) or True

        if self.debug:
            sys.path.append(os.path.join(sys.prefix, "pycharm-debug.egg"))
            import pydevd

            pydevd.settrace('localhost', port=43234, stdoutToServer=True, stderrToServer=True)
            log.startLogging(sys.stdout)
        else:
            log.startLogging(open('./log/service.out.txt', 'w'))

        # Change to our dir
        main_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
        os.chdir(main_dir)
        sys.path.append(main_dir)

        import webservice

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        webservice.main()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def main(rdebug=False):
    args = sys.argv
    if args[1].lower() == "rdebug":
        args.append("debug")
        args[1] = "restart"
    print args
    win32serviceutil.HandleCommandLine(AppServerSvc, os.path.realpath(__file__)[:-3] + ".AppServerSvc", args)