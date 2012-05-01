
import os

from cubicus.sock import SocketThread
from cubicus.models import Application, Context
from cubicus.models import Event

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
                # Make sure the application comes to foreground in any case
                self.queue_message('become_active')

        elif name == 'event':
            event = new_value
            if event.source != Event.APP_EVENT and \
               event.application_id == self._app.application_id:
                # Event originated elsewhere and is intended for this
                # app, so forward it
                self.queue_message('event', event.to_json())

    def allowed_types(self):
        types = ['application_identify', 'switch_context', 'event',
                 'became_active']
        return SocketThread.allowed_types(self) + types

    def handle_became_active(self):
        if self._app:
            app_id = self._app.application_id
            # Switch to this application remotely if it's not already active
            if self.manager.current_application != app_id:
                self.manager.current_application = app_id

                # Switch to default (or first) of this app's contexts
                cid = None
                if self._app.default_context is not None:
                    cid = self._app.default_context
                else:
                    cid = self._app.contexts[0].context_id
                self.manager.current_context = cid

    def handle_application_identify(self, json_app):
        app = Application.from_json(json_app)
        self.manager.add_application(app)
        self._app = app

    def handle_switch_context(self, context_id):
        self.manager.current_context = context_id

    def handle_event(self, json_event):
        event = Event.from_json(json_event)

        # App has no knowledge of its application_id, so set it here
        event.application_id = self._app.application_id
        
        # Indicate that the event came from an app socket
        event.source = Event.APP_EVENT
        self.manager.send_event(event)

