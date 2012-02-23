
from threading import Thread
from cubicus.utils import LogMixin

class ApplicationSocketThread(Thread, LogMixin):
    """
    Accepts a socket to a local Cubicus-enabled application and services it
    """
    def __init__(self, clientsocket):
        Thread.__init__(self)
        self._sock = clientsocket
        self.daemon = True
        self._continue = True

    def stop(self):
        self._continue = False

    def run(self):
        sock = self._sock
        self.log('Spawned')

        self.log('Sending...')
        sock.send('hello')
        
        #self.log('Receiving...')
        #res = sock.recv(1024)
        #self.log('Got "%s"' res)
                    
        self.log('Closing')
        sock.close()

