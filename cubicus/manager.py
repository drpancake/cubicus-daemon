
class Application(object):
    def __init__(self):
        self._id = None
        self._contexts = None
        self._name = None

    def to_json(self):
        b1 = {'type': 'button', 'id': 1, 'ratio': 0.25, 'label': 'My Label'}
        c1 = {'type': 'canvas', 'id': 2, 'ratio': 0.75}
        l1 = {'type': 'hbox', 'id': 3, 'ratio': 1, 'items': [b1, c1]}
        return {'id': 1, 'contexts': [{'id': 1, 'layout': l1}]}

class Context(object):
    def __init__(self):
        self._id = None
        self._layout = None

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

