
from observable import Observable, new_attribute

class LayoutElement(Observable):
    def __init__(self, element_id, element_type, ratio, ** params):
        Observable.__init__(self)
        self.element_id = element_id
        self.element_type = element_type
        self.ratio = ratio
        self._params = params

    @staticmethod
    def from_json(d):
        id_ = d.pop('id')
        type_ = d.pop('type')
        ratio = d.pop('ratio')
        
        # Params is any remaining keys we haven't yet popped
        params = d

        if type_ in ['hbox', 'vbox']:
            return Box(id_, type_, ratio, ** params)
        elif type_ == 'canvas':
            return Canvas(id_, type_, ratio, ** params)
        else:
            return LayoutElement(id_, type_, ratio, ** params)

    def to_json(self):
        d = {'id': self.element_id, 'type': self.element_type,
             'ratio': self.ratio}
        return d

class Box(LayoutElement):
    def __init__(self, element_id, element_type, ratio, ** params):
        LayoutElement.__init__(self, element_id, element_type, ratio, ** params)
        self.items = map(lambda item: LayoutElement.from_json(item),
                         params['items'])
    
    def to_json(self):
        # Augment base element JSON with each child item's JSON
        d = LayoutElement.to_json(self)
        d['items'] = map(lambda item: item.to_json(), self.items)
        return d

class Canvas(LayoutElement):
    paths = new_attribute('paths', [])

    def add_path(self, points):
        self.paths += [points]

    def clear(self):
        pass

