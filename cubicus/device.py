
import os

from cubicus.utils import SocketThread
from cubicus.models import Event

class DeviceSocketThread(SocketThread):
    """
    Accepts a socket to a remote Cubicus device and services it
    """
    def __init__(self, clientsocket):
        SocketThread.__init__(self, clientsocket)
        self._paired = False

        # Subscribe to manager updates
        self.manager.subscribe(self)

    def notify(self, obj, name, new_value):
        print '%s got %s => %s' % (self, name, new_value)
        if name in ['current_context', 'current_application']:
            self.send_state()

    def allowed_types(self):
        types = ['device_identify', 'state', 'event']
        return SocketThread.allowed_types(self) + types

    def send_applications(self):
        apps = map(lambda a: a.to_json(), self.manager.applications)
        self.queue_message('applications', apps)

    def handle_device_identify(self, guid):
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
        self.send_applications()
        self.send_state()

    def handle_state(self, state):
        self.manager.current_application = state['current_application']
        self.manager.current_context = state['current_context']

    def handle_event(self, event):
        self.manager.send_event(Event.from_json(event))

