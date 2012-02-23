
import select
import socket
from threading import Thread

class LogMixin:
    def log(self, s):
        print '[%s: %s] %s' % (self.__class__.__name__, self.name, s)

class Singleton(type):
    """
    To turn any class into a singleton:
    __metaclass__ = Singleton

    See: http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ConnectionListener(Thread, LogMixin):
    """
    Listens for incoming connections and instantiates the class given by
    client_cls (Thread subclass implementing at least a stop() method)
    to service a new client.
    """
    def __init__(self, port, client_cls):
        Thread.__init__(self)
        self.daemon = True
        self._port = port
        self._cls = client_cls
        self._continue = True
        self._threads = []

    def stop(self):
        self._continue = False

    def run(self):
        # Open the socket
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((socket.gethostname(), self._port))
        serversocket.listen(5) # 5 queued max

        self.log('Waiting for clients')
        try:
            while self._continue:
                # Non-blocking accept() so we can gracefully close
                # serversocket and any device threads we've spawned
                res = accept_with_timeout(serversocket, 0.3)
                if res:
                    (clientsocket, address) = res
                    self.log('New client: %s %s' % (clientsocket, address))
                    t = self._cls(clientsocket)
                    self._threads.append(t)
                    t.start()
        finally:
            self.log('Stopping')
            for t in self._threads:
                t.stop()
                t.join()
            serversocket.close()

def accept_with_timeout(serversocket, timeout):
    """
    See: http://stackoverflow.com/questions/1148062/python-socket-accept-blocks
         -prevents-app-from-quitting/1148237#1148237

    Waits 'timeout' seconds to return a new connection tuple, otherwise
    returns None
    """
    readable, writable, err = select.select([serversocket], [], [], timeout)
    if readable:
        return serversocket.accept()
    else:
        return None

