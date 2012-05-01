
import os
import random

from cubicus.sock import SocketThread
from cubicus.models import Event

PAIRINGS_FILE = 'pairings.dat'

def display_pin(pin):
    """ Kludge - PIL for now """
    from PIL import Image, ImageDraw
    im = Image.new('RGBA', (300, 100))
    draw = ImageDraw.Draw(im)
    draw.text((5, 5), pin)
    im.show()

class DeviceSocketThread(SocketThread):
    """
    Accepts a socket to a remote Cubicus device and services it
    """
    def __init__(self, clientsocket):
        SocketThread.__init__(self, clientsocket)
        self._paired = False
        self._challenged_guid = None
        self._pin = None

        # Subscribe to manager updates
        self.manager.subscribe(self)

    def notify(self, obj, name, new_value):
        if name in ['current_context', 'current_application']:
            self.send_state()
        elif name == 'event':
            event = new_value
            if event.source != Event.DEVICE_EVENT:
                # Event originated elsewhere, so forward it
                # to the device
                self.queue_message('event', event.to_json())

    def allowed_types(self):
        types = ['device_identify', 'state', 'event', 'pair_response']
        return SocketThread.allowed_types(self) + types

    def send_applications(self):
        apps = map(lambda a: a.to_json(), self.manager.applications)
        self.queue_message('applications', apps)

    def handle_pair_response(self, pin):
        if pin == self._pin:
            # Successfully paired so store the GUID
            fp = open(PAIRINGS_FILE, 'w')
            fp.write('%s\n' % self._challenged_guid)
            fp.close()

            # Continue to next step
            self._paired = True
            self.send_applications()
            self.send_state()
        else:
            self.queue_message('pair_failure')
            self.stop()

    def handle_device_identify(self, guid):
        """
        Checks for existing pairing with the given GUID. If none
        exists, initiate the pairing process. Once paired, queues
        the remaining handshake messages
        """
        assert self._paired is False

        # Touch if its not there
        if not os.path.isfile(PAIRINGS_FILE):
            open(PAIRINGS_FILE, 'w').close()

        fp = open(PAIRINGS_FILE, 'r')
        s = fp.read()
        fp.close()
        pairs = s.split('\n')

        if guid not in pairs:
            # Unknown GUID so challenge for a random PIN number
            self.log('Need to pair for "%s"' % guid)
            self._challenged_guid = guid
            self._pin = ''.join(map(str, [random.randint(0, 9)
                                          for i in range(4)]))
            display_pin(self._pin) # Display on host machine
            self.queue_message('pair_request')
        else:
            # Already paired, continue to next step
            self._paired = True
            self.send_applications()
            self.send_state()

    def handle_state(self, state):
        self.manager.current_application = state['current_application']
        self.manager.current_context = state['current_context']

    def handle_event(self, json_event):
        event = Event.from_json(json_event)
        event.source = Event.DEVICE_EVENT
        self.manager.send_event(event)

