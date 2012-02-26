#!/usr/bin/env python

import select
import sys
import socket
import time
from threading import Thread
import pybonjour

from cubicus.device import DeviceSocketThread
from cubicus.host import ApplicationSocketThread
from cubicus.utils import LogMixin, ConnectionListener

class BonjourService(Thread, LogMixin):
    """
    Advertises an open port via Bonjour
    """
    def __init__(self, name, regtype, port):
        Thread.__init__(self)
        self._name = name
        self._regtype = regtype
        self._port = port
        self._continue = True
        self.daemon = True

    def stop(self):
        self._continue = False

    def _reg_callback(self, sdRef, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            self.log('Registered service: name=%s, regtype=%s, domain=%s' %
                     (name, regtype, domain))

    def run(self):
        sdRef = pybonjour.DNSServiceRegister(name=self._name,
                                             regtype=self._regtype,
                                             port = self._port,
                                             callBack = self._reg_callback)
        try:
            while self._continue:
                timeout = 0.3
                ready = select.select([sdRef], [], [], timeout)
                if sdRef in ready[0]:
                    pybonjour.DNSServiceProcessResult(sdRef)
        finally:
            self.log('Stopping')
            sdRef.close()

class ApplicationListener(ConnectionListener):
    pass

class DeviceListener(ConnectionListener):
    pass


if __name__ == '__main__':
    name = 'TestService'
    regtype = '_test._tcp'
    device_port = 1234
    app_port = 28739

    # Listener for Bonjour broadcasts
    bonjour_service = BonjourService(name, regtype, device_port)
    
    # Listeners for applications/devices
    app_listener = ApplicationListener(app_port, ApplicationSocketThread,
                                       host='localhost')
    device_listener = DeviceListener(device_port, DeviceSocketThread)

    threads = [bonjour_service, app_listener, device_listener]
    map(lambda t: t.start(), threads)

    # All threads are daemonic so block here until ctrl-c
    try:
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        print 'Quitting...'
        # Keep main thread alive until all threads have stopped
        for t in threads:
            t.stop()
            t.join()

