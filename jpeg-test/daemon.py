import select
import sys
import threading
import socket
from StringIO import StringIO

import pybonjour
from PIL import Image

class BonjourService(threading.Thread):
    def __init__(self, name, regtype, port):
        threading.Thread.__init__(self)
        self._name = name
        self._regtype = regtype
        self._port = port
        self._continue = True
        self.daemon = True

    def _reg_callback(self, sdRef, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print 'Registered service:'
            print '  name    =', name
            print '  regtype =', regtype
            print '  domain  =', domain

    def run(self):
        sdRef = pybonjour.DNSServiceRegister(name=self._name,
                                             regtype=self._regtype,
                                             port = self._port,
                                             callBack = self._reg_callback)
        try:
            while self._continue:
                ready = select.select([sdRef], [], [])
                if sdRef in ready[0]:
                    pybonjour.DNSServiceProcessResult(sdRef)
        finally:
            sdRef.close()

JPEGS = []
for i in range(1, 5):
    im = Image.open(file('waterfall%s.jpg' % i))
    fp = StringIO()
    im.save(fp, 'JPEG')
    fp.seek(0)
    JPEGS.append(fp.read())

class CubicusThread(threading.Thread):
    def __init__(self, clientsocket):
        threading.Thread.__init__(self)
        self._sock = clientsocket
        self.daemon = True

    def run(self):
        sock = self._sock
        # Say hello
        #print 'Saying hello...'
        #sock.send('hello')

        print 'Sending JPGs...'
        #sock.send(',jpg:')

        MARKER = ',' * 5
        for i in range(500):
            for jpeg in JPEGS:
                print 'Sending JPG, len = %s' % len(jpeg)
                sock.send(jpeg)
                sock.send(MARKER) # 0x2c
            
        #sock.send(',bye')

        print 'Closing...'
        sock.close()
        
        #print 'Receiving...'
        #res = sock.recv(1024)
        #print 'Got: %s' % res


def cubicus_listen(port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((socket.gethostname(), port))
    # Queue 5 incoming conns max
    serversocket.listen(5)
    
    try:
        while 1:
            print 'Waiting for clients...'
            (clientsocket, address) = serversocket.accept()
            print 'New client: %s %s' % (clientsocket, address)
            ct = CubicusThread(clientsocket)
            ct.start()
    except KeyboardInterrupt:
        pass
    finally:
        serversocket.close()

if __name__ == '__main__':
    name = 'TestService'
    regtype = '_test._tcp'
    port = 1234

    bonjour_thread = BonjourService(name, regtype, port)
    bonjour_thread.start()
    
    cubicus_listen(port)

