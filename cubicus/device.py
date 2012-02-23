
from threading import Thread
from Queue import Queue
import socket
import json
import os
import select
import time

from cubicus.manager import Manager
from cubicus.utils import LogMixin, accept_with_timeout
from cubicus.constants import LINE_DELIMITER

class DeviceSocketThread(Thread, LogMixin):
    """
    Accepts a socket to a remote Cubicus device and services it
    """
    ALLOWED_TYPES = ['identify']

    def __init__(self, clientsocket):
        Thread.__init__(self)
        self._sock = clientsocket
        self._sendqueue = Queue()
        self._paired = False
        self._manager = Manager()
        self.daemon = True
        self._continue = True

    def stop(self):
        self._continue = False

    def _parse(self, s):
        self.log('Got message: "%s"' % s)
        # Dispatch to a handler method
        msg = json.loads(s)
        assert msg['type'] in self.ALLOWED_TYPES
        try:
            method = getattr(self, '_handle_%s' % msg['type'])
            method(msg['content'])
        except AttributeError, e:
            # TODO: handle this
            pass

    def _queue_message(self, type_, content):
        msg = {
            'type': type_,
            'content': content
        }
        s = json.dumps(msg)
        self._sendqueue.put(s + LINE_DELIMITER)

    def _send_applications(self):
        apps = self._manager.get_applications()
        self._queue_message('applications', apps)

    def _send_state(self):
        state = self._manager.get_state()
        self._queue_message('state', state)

    def _handle_identify(self, guid):
        """
        Checks for existing pairing with the given GUID. If none
        exists, initiate the pairing process. Once paired, queues
        the remaining handshake messages
        """
        assert self._paired is False
        pairings_fil = 'pairings.dat'

        # Touch if its not there
        if not os.path.isfile(pairings_fil):
            open(pairings_fil, 'w').close()

        fp = open(pairings_fil, 'r')
        s = fp.read()
        fp.close()
        pairs = s.split('\n')
        if guid not in pairs:
            # TODO: pairing process starts
            # could use 'expected' array for recv
            self.log('Need to pair! continuing anyway')
            self._paired = True

        # Once we're paired, next step is to send 'applications'
        # and 'state' messages
        self._send_applications()
        self._send_state()

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

