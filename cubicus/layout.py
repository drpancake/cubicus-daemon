
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
        elif type_ == 'button':
            return Button(id_, type_, ratio, ** params)
        elif type_ == 'accelerator':
            return Accelerator(id_, type_, ratio, ** params)
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
        # Find the element the event is intended for, if it's a button
        # we need to take button groups into account
        elements = filter(lambda item: item.element_id == event.element_id,
                          self.items)
        assert len(elements) == 1
        el = elements[0]
        if el.element_type == 'button' and el.group is not None:
            # Special case for buttons in a group (i.e. radio buttons)

            # Note: the intended button still gets passed the event
            # and thus selects itself
            
            # Grab all _other_ buttons in the group and ensure that
            # they are deselected
            buttons = filter(lambda item: item.element_type == 'button' and \
                             item.group == el.group and item != el, self.items)
            for button in buttons:
                button.selected = False

        # Unconditionally pass event to all child items
        map(lambda item: item.send_event(event), self.items)
    
    def to_json(self):
        # Augment base element JSON with each child item's JSON
        d = LayoutElement.to_json(self)
        d['items'] = map(lambda item: item.to_json(), self.items)
        return d

class Canvas(LayoutElement):
    def __init__(self, element_id, element_type, ratio, ** params):
        LayoutElement.__init__(self, element_id, element_type, ratio, ** params)
        self.points = params.get('points', [])
        self.color = params.get('color', None)

    def send_event(self, event):
        if event.element_id == self.element_id:
            if 'points' in event.content:
                self.points += event.content['points']
            elif 'color' in event.content:
                self.color = event.content['color']

    def clear(self):
        pass

    def to_json(self):
        # Augment base element JSON
        d = LayoutElement.to_json(self)
        d['points'] = self.points
        d['color'] = self.color
        return d

class Button(LayoutElement):
    def __init__(self, element_id, element_type, ratio, ** params):
        LayoutElement.__init__(self, element_id, element_type, ratio, ** params)
        self.label = params['label']
        self.selected = params['selected']
        self.group = params.get('group')

    def to_json(self):
        # Augment base element JSON with each child item's JSON
        d = LayoutElement.to_json(self)
        d['label'] = self.label
        d['selected'] = self.selected
        if self.group is not None:
            d['group'] = self.group
        return d

    def send_event(self, event):
        # Assume this is a 'selected' event
        if event.element_id == self.element_id:
            self.selected = event.content['selected']

class Accelerator(LayoutElement):
    def __init__(self, element_id, element_type, ratio, ** params):
        LayoutElement.__init__(self, element_id, element_type, ratio, ** params)

    def send_event(self, event):
        # No need to store acceleration events
        pass

