
import os

from cubicus.utils import SocketThread
from cubicus.models import Application, Context

class ApplicationSocketThread(SocketThread):
    """
    Accepts a socket to a local Cubicus-enabled application and services it
    """
    def __init__(self, clientsocket):
        SocketThread.__init__(self, clientsocket)
        self._app = None
        # Subscribe to manager updates
        self.manager.subscribe(self)

    def notify(self, obj, name, new_value):
        if name in ['current_application', 'current_context'] and self._app:
            # Notify app of changed context if we're the currently
            # active application ID
            man = self.manager
            if man.current_application == self._app.application_id:
                self.queue_message('switch_context', man.current_context)

    def allowed_types(self):
        types = ['application_identify', 'switch_context']
        return SocketThread.allowed_types(self) + types

    def handle_application_identify(self, json_app):
        app = Application.from_json(json_app)
        self.manager.add_application(app)
        self._app = app

    def handle_switch_context(self, context_id):
        self.manager.current_context = context_id

