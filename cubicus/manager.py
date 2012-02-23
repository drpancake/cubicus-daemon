
from cubicus.utils import Singleton

class Manager(object):
    """
    Keeps track of current applications and their layouts,
    states, etc.

    Note: implemented as a thread-safe singleton for sharing
    between threads
    """
    __metaclass__ = Singleton
    
    def __init__(self):
        print 'I am manager! 0x%s' % hex(id(self))

    def get_applications(self):
        # TODO should probably have classes Application, Context,
        # Layout, etc

        class Bla:
            i = 1
            def __call__(self):
                self.i += 1
                return self.i
        make_id = Bla()

        b1 = {'type': 'button', 'id': make_id(), 'ratio': 0.25, 'label': 'My Label'}
        c1 = {'type': 'canvas', 'id': make_id(), 'ratio': 0.75}
        l1 = {'type': 'hbox', 'id': make_id(), 'ratio': 1, 'items': [b1, c1]}

        b2 = {'type': 'button', 'id': make_id(), 'ratio': 0.5, 'label': 'My Label'}
        c2 = {'type': 'canvas', 'id': make_id(), 'ratio': 0.5}
        l2 = {'type': 'hbox', 'id': make_id(), 'ratio': 1, 'items': [b2, c2]}


        app1 = {'id': 1 ,'contexts': [{'id': 1, 'layout': l1},
                                      {'id': 2, 'layout': l2}]}
        apps = [app1]
        return apps

    def get_state(self):
        state = {'current_application': 1, 'current_context': 1}
        # 'contexts' key not included for now (its optional)
        return state

    # TODO: manager could throw events when applications/state changes

