
from cubicus.utils import IDGenerator
from cubicus.layout import LayoutElement

class Context(object):
    def __init__(self, context_id, layout):
        self.context_id = context_id
        self.layout = layout

    def send_event(self, event):
        if event.context_id == self.context_id:
            self.layout.send_event(event)

    @staticmethod
    def from_json(d):
        id_ = d['id']
        layout = LayoutElement.from_json(d['layout'])
        return Context(id_, layout)

    def to_json(self):
        return {'id': self.context_id, 'layout': self.layout.to_json()}

class Application(object):
    id_generator = IDGenerator()
    
    def __init__(self, application_id, default_context, name, contexts):
        self.application_id = application_id
        self.default_context = default_context
        self.name = name
        self.contexts = contexts

    def send_event(self, event):
        if event.application_id == self.application_id:
            print 'app %s accepted event: %s' % (self, event)
            map(lambda c: c.send_event(event), self.contexts)

    @staticmethod
    def from_json(d):
        """
        Expects content from an 'application_identify' message
        """
        name = d['name']
        default = d.get('default_context') # optional
        contexts = map(lambda c: Context.from_json(c), d['contexts'])
        app_id = Application.id_generator.new_id()
        return Application(app_id, default, name, contexts)

    def to_json(self):
        contexts = map(lambda c: c.to_json(), self.contexts)
        return {'id': self.application_id, 'contexts': contexts}

    #def to_json(self):
        #b1 = {'type': 'button', 'id': 1, 'ratio': 0.25, 'label': 'My Label'}
        #c1 = {'type': 'canvas', 'id': 2, 'ratio': 0.75}
        #l1 = {'type': 'hbox', 'id': 3, 'ratio': 1, 'items': [b1, c1]}
        #return {'id': 1, 'contexts': [{'id': 1, 'layout': l1}]}

class Event(object):
    DEVICE_EVENT = 1
    APP_EVENT = 2

    def __init__(self, application_id, context_id, element_id,
                 content, source=None):
        """
        event_source = DEVICE_EVENT or APP_EVENT
        """
        self.application_id = application_id
        self.context_id = context_id
        self.element_id = element_id
        self.content = content
        self.source = source
        
    @staticmethod
    def from_json(d):
        return Event(** d)

    def to_json(self):
        return {'application_id': self.application_id,
                'context_id': self.context_id, 'element_id': self.element_id,
                'content': self.content}

