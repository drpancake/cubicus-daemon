
import select

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

class IDGenerator(object):
    """
    For generating unique IDs across all instances of a class
    """
    def __init__(self):
        self._id = 0

    def new_id(self):
        self._id += 1
        return self._id

class LogMixin:
    def log(self, s):
        print '[%s: %s] %s' % (self.__class__.__name__, self.name, s)

