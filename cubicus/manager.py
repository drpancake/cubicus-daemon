
from observable import Observable, new_attribute

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

class Manager(Observable):
    """
    Keeps track of current applications and their layouts,
    states, etc.

    Note: implemented as a thread-safe singleton for sharing
    between threads
    """
    __metaclass__ = Singleton

    current_context = new_attribute('current_context')
    current_application = new_attribute('current_application')
    applications = new_attribute('applications', [])
    
    def __init__(self):
        Observable.__init__(self)

    def add_application(self, app):
        # Brand new list so notify() is triggered
        self.applications += [app]

    def remove_application(self, app):
        # Brand new list so notify() is triggered
        self.applications = filter(lambda a: a != app, self.applications)

