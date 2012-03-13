
class LayoutElement(object):
    def __init__(self, element_id, element_type, ratio, ** params):
        self.element_id = element_id
        self.element_type = element_type
        self.ratio = ratio
        self._params = params

    def send_event(self, event):
        if event.element_id == self.element_id:
            print '[!!!] Unhandled event for %s (%s)' % (self, event)

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
        # Inflate child items
        self.items = [LayoutElement.from_json(item) for item in params['items']]

    def send_event(self, event):
        map(lambda item: item.send_event(event), self.items)
    
    def to_json(self):
        # Augment base element JSON with each child item's JSON
        d = LayoutElement.to_json(self)
        d['items'] = map(lambda item: item.to_json(), self.items)
        return d

class Canvas(LayoutElement):
    def __init__(self, element_id, element_type, ratio, ** params):
        LayoutElement.__init__(self, element_id, element_type, ratio, ** params)
        self._paths = []

    def send_event(self, event):
        if event.element_id == self.element_id:
            print 'Canvas got event: %s' % event
            #self.add_path([(0, 0), (5, 5)])

    def add_path(self, points):
        self._paths.append(points)

    def clear(self):
        pass

