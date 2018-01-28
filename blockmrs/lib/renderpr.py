from .html import XHTML

h = XHTML()

class XMLDataType:
    xmlname = None

    def __init__(self, elem):
        self.elem = elem

class Namespace(XMLDataType):
    name = 'No Name'
    icon = None
    button_klass = 'ns-button'
    buttons_klass = 'ns-buttons well clearfix'
    fields_klass = 'ns-fields panel panel-default'
    view_klass = 'ns-view'
    link_klass = 'ns-link'

    def __init__(self, elem):
        self.fields = list(map(match_field, elem))
        super().__init__(elem)

    def render(self):
        d = h.div(klass=self.button_klass)
        inner_d = h.div()
        inner_d += h.i(klass=' '.join(['fa', 'fa-5x', self.icon]))
        text = h.div(klass=self.link_klass)
        text += self.name
        inner_d += text
        d += inner_d
        a = h.a(href=self.xmlname + '/')
        a += d
        return a

    def render_view(self):
        d = h.div(klass=self.view_klass)
        fields_panel = h.div(klass=self.fields_klass)
        heading = h.div(klass='panel-heading')
        title = h.h3(klass='panel-title')
        title += h.i(klass=' '.join(['fa', self.icon]))
        title += ' ' + self.name
        heading += title
        fields_panel += heading
        fields_ul = h.ul(klass='list-group')
        buttons_d = h.div(klass=self.buttons_klass)
        for field in (f for f in self.fields if isinstance(f, Field)):
            wrapper = h.li(klass='list-group-item')
            wrapper += field.render()
            fields_ul += wrapper
        for btn in (f for f in self.fields if isinstance(f, Namespace)):
            buttons_d += btn.render()
        fields_panel += fields_ul
        d += fields_panel
        d += buttons_d
        return d

class Field(XMLDataType):
    name = None

    # overrride PLEASE
    def render(self, ht=None):
        dl = h.dl(klass='dl-horizontal')
        dt = h.dt()
        dt += self.name
        dl += dt
        dd = h.dd()
        dd += ht if ht else self.elem.text
        dl += dd
        return dl

class PatientHome(Namespace):
    xmlname = 'patient'
    name = 'Patient Information'
    icon = 'fa-user-circle'

class PersonalInformation(Namespace):
    xmlname = 'personal_information'
    name = 'Personal Information'
    icon = 'fa-id-card'

class ContactInformation(Namespace):
    xmlname = 'contacts'
    name = 'Contact Information'
    icon = 'fa-address-book'

class Billing(Namespace):
    xmlname = 'billing'
    name = 'Billing Information'
    icon = 'fa-gavel'

class Records(Namespace):
    xmlname = 'medical'
    name = 'Medical Records'
    icon = 'fa-heartbeat'

class PatientID(Field):
    xmlname = 'patient_id'
    name = 'Patient ID'

class Name(Field):
    xmlname = 'name'
    name = 'Name'

    def __init__(self, elem):
        self.family = elem.get('family')
        self.given = elem.get('given')
        self.preferred = elem.get('preferred')

    def render(self):
        fmt_string = '{}, {}'
        if self.preferred:
            fmt_string += ' ({})'
        return super().render(ht=fmt_string.format(self.family, self.given, self.preferred))

fields = {k.xmlname: k for k in globals().values() if hasattr(k, 'xmlname')}

def match_field(elem):
    return fields.get(elem.tag, Field)(elem)
