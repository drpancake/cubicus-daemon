
import os
from cubicus.utils import SocketThread

class ApplicationSocketThread(SocketThread):
    """
    Accepts a socket to a local Cubicus-enabled application and services it
    """
    #def __init__(self, clientsocket):
        #SocketThread.__init__(self, clientsocket)

    def allowed_types(self):
        types = ['application_identify', 'switch_context']
        return SocketThread.allowed_types(self) + types

    def handle_application_identify(self, contexts):
        pass
        # TODO: context to Context objects? pass to manager

    def handle_switch_context(self, context_id):
        pass

