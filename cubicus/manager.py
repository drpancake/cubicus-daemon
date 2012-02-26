
#from cubicus.utils import IDGenerator

class IDGenerator(object):
    """
    For generating unique IDs across all instances of a class
    """
    def __init__(self):
        self._id = 0

    def new_id(self):
        self._id += 1
        return self._id

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


class Application(object):
    id_generator = IDGenerator()
    
    def __init__(self, application_id, default_context, name, contexts):
        # TODO: @property for these?
        self.application_id = application_id
        self.default_context = default_context
        self.name = name
        self.contexts = contexts

    @staticmethod
    def from_json(d):
        """
        Expects content from an 'application_identify' message
        """
        name = d['name']
        default = d['default_context']
        contexts = map(lambda c: Context.from_json(c), d['contexts'])
        app_id = Application.id_generator.new_id()
        return Application(app_id, default, name, contexts)

    def to_json(self):
        b1 = {'type': 'button', 'id': 1, 'ratio': 0.25, 'label': 'My Label'}
        c1 = {'type': 'canvas', 'id': 2, 'ratio': 0.75}
        l1 = {'type': 'hbox', 'id': 3, 'ratio': 1, 'items': [b1, c1]}
        return {'id': 1, 'contexts': [{'id': 1, 'layout': l1}]}


class Context(object):
    id_generator = IDGenerator()

    def __init__(self, context_id, layout):
        self.context_id = context_id
        self.layout = layout

    @staticmethod
    def from_json(d):
        return Context(Context.id_generator.new_id(), None)


class Manager(object):
    """
    Keeps track of current applications and their layouts,
    states, etc.

    Note: implemented as a thread-safe singleton for sharing
    between threads
    """
    __metaclass__ = Singleton
    
    def __init__(self):
        self._applications = []
        self._current_application = None
        self._current_context = None

    def add_application(self, app):
        self._applications.append(app)
        # TODO: notify devices

    def remove_application(self, app):
        # TODO
        pass
    
    @property
    def applications(self):
        #b1 = {'type': 'button', 'id': make_id(), 'ratio': 0.25, 'label': 'My Label'}
        #c1 = {'type': 'canvas', 'id': make_id(), 'ratio': 0.75}
        #l1 = {'type': 'hbox', 'id': make_id(), 'ratio': 1, 'items': [b1, c1]}
        #b2 = {'type': 'button', 'id': make_id(), 'ratio': 0.5, 'label': 'My Label'}
        #c2 = {'type': 'canvas', 'id': make_id(), 'ratio': 0.5}
        #l2 = {'type': 'hbox', 'id': make_id(), 'ratio': 1, 'items': [b2, c2]}
        self._applications = [Application()]
        return self._applications

    @property
    def current_application(self):
        #return self._current_application
        return 1

    @property
    def current_context(self):
        #return self._current_context
        return 1

