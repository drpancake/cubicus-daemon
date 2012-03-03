
import select
import socket
import time
import json
from threading import Thread
from Queue import Queue

from cubicus.manager import Manager
from cubicus.constants import LINE_DELIMITER

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

class ConnectionListener(Thread, LogMixin):
    """
    Listens for incoming connections and instantiates the class given by
    client_cls (Thread subclass implementing at least a stop() method)
    to service a new client.
    """
    def __init__(self, port, client_cls, host=None):
        Thread.__init__(self)
        self.daemon = True
        self._port = port
        self._cls = client_cls
        self._continue = True
        self._threads = []
        self._host = host

    def stop(self):
        self._continue = False

    def run(self):
        # Open the socket
        if self._host is None:
            self._host = socket.gethostname()
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        serversocket.bind((self._host, self._port))
        serversocket.listen(5) # 5 queued max

        self.log('Waiting for clients @ %s:%s' % (self._host, self._port))
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

class SocketThread(Thread, LogMixin):
    def __init__(self, clientsocket):
        Thread.__init__(self)
        self._sock = clientsocket
        self._sendqueue = Queue()
        self.manager = Manager()
        self.daemon = True
        self._continue = True

    def allowed_types(self):
        return []

    def stop(self):
        self._continue = False

    def _parse(self, s):
        self.log('Got message: "%s"' % s)
        # Dispatch to a handler method
        msg = json.loads(s)
        assert msg['type'] in self.allowed_types()
        try:
            method = getattr(self, 'handle_%s' % msg['type'])
            method(msg['content'])
        except AttributeError, e:
            # TODO: handle this
            pass

    def queue_message(self, type_, content):
        msg = {
            'type': type_,
            'content': content
        }
        s = json.dumps(msg)
        self._sendqueue.put(s + LINE_DELIMITER)

    def send_state(self):
        a = self.manager.current_application
        c = self.manager.current_context
        # Only send if both are set
        if a != None and c != None:
            state = {'current_application': a, 'current_context': c}
            self.queue_message('state', state)

    def run(self):
        sock = self._sock
        self.log('Spawned')

        # Non-blocking mode
        sock.setblocking(0)
        
        buffered = ''
        while self._continue:
            # Service the send queue
            while not self._sendqueue.empty():
                # TODO: might be best to pop a single item from the queue on
                # each pass in case send() gets overwhelmed (e.g. buffer full)
                msg = self._sendqueue.get()
                self.log('Sending: "%s"' % msg)
                sock.send(msg)
           
            try:
                res = sock.recv(4096)
                if not res:
                    break # FIN
            except socket.error, e:
                # TODO: use select.select() to block until _sendqueue has data
                # or socket is readable (more efficient)

                # In non-blocking mode recv() throws an error if there's nothing
                # to read. Catch it and wait a bit so we don't thrash the CPU
                assert e.errno == 35, 'Expecting errno 35 for nothing to read'
                time.sleep(0.1) # Wait a bit
                continue

            if LINE_DELIMITER not in res:
                # No delimiter so this is an incomplete message
                buffered += res
            else:
                parts = res.split(LINE_DELIMITER)
                if len(parts) == 2 and parts[-1] == '':
                    # Delimiter was at the end e.g. 'blabla\r\n'
                    message = buffered + parts[0]
                    buffered = ''
                    self._parse(message)
                else:
                    # If ending is a delimiter we have multiple
                    # complete messages, but most likely the last
                    # part needs to be buffered (after dealing with
                    # the parts before it)
                    trailer = parts.pop(-1)
                    for part in parts:
                        if buffered:
                            message = buffered + part
                            buffered = ''
                        else:
                            message = part
                        self._parse(message)
                    if trailer != '':
                        buffered = trailer
            
        self.log('Stopping')
        sock.close()

