
from cubicus.utils import IDGenerator

class LayoutElement(object):
    def __init__(self, element_id, element_type, ratio, ** params):
        self.element_id = element_id
        self.element_type = element_type
        self.ratio = ratio
        self._params = params

    @staticmethod
    def from_json(d):
        id_ = d.pop('id')
        type_ = d.pop('type')
        ratio = d.pop('ratio')
        
        params = {}
        # Convert items to models if we have it
        if 'items' in d:
            items = map(lambda item: LayoutElement.from_json(item),
                        d.pop('items'))
            params['items'] = items
        # Anything else goes in params
        params.update(d)

        return LayoutElement(id_, type_, ratio, ** params)

    def to_json(self):
        d = {'id': self.element_id, 'type': self.element_type,
             'ratio': self.ratio}

        items = None
        if self._params and 'items' in self._params:
            items = map(lambda item: item.to_json(), self._params['items'])
            d['items'] = items

        for k, v in self._params.items():
            if k != 'items':
                d[k] = v
        return d

class Context(object):
    def __init__(self, context_id, layout):
        self.context_id = context_id
        self.layout = layout

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

