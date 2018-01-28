"""Portal controller module"""

from tg import expose, request, abort, redirect, predicates
from xml.etree import ElementTree as ET
import uuid

from blockmrs.lib.base import BaseController
from blockmrs.model import DBSession, User, PrivateKey
from blockmrs.lib.renderpr import match_field
from blockmrs.lib.records import retrieve_record, store_record
from xml.dom import minidom


__all__ = ['UserPortalController']

class NamespaceViewController(BaseController):
    def __init__(self, nselem, name):
        self.nselem = nselem
        self.name = name

    @expose('blockmrs.templates.portal')
    def _default(self):
        """Handle the user's profile page."""
        return dict(page='profile', view=match_field(self.nselem), name=self.name)

class NamespaceEditController(BaseController):
    def __init__(self, root, xpath, user, record):
        self.root = root
        self.xpath = xpath
        self.user = user
        self.record = record

    @expose('blockmrs.templates.edit')
    def _default(self):
        root = ET.fromstring(self.record)
        node = root.find(self.xpath)
        if request.method == 'POST':
            try:
                new_node = ET.fromstring(request.POST['editor'])
            except:
                abort(500, 'You made a mistake writing the XML.')
            node.clear()
            for ch in new_node:
                node.append(ch)
            node.attrib = new_node.attrib
            pk, blockchain_id = store_record(ET.tostring(root), b'foobar')
            self.user.blockchain_id_cache = blockchain_id
            private_key = PrivateKey(user_id=self.user.id, blockchain_id=blockchain_id, private_key=pk)
            DBSession.add(private_key)
            DBSession.add(self.user)
            redirect('/p/' + self.xpath[2:] + '/')

        return dict(page='profile', content=minidom.parseString(ET.tostring(node)).toprettyxml(indent="  ").partition('\n')[2], xpath=self.xpath)

class UserPortalController(BaseController):
    allow_only = predicates.not_anonymous()

    @expose()
    def _lookup(self, *args):
        uname = request.identity['repoze.who.userid']

        user = DBSession.query(User) \
                        .filter(User.user_name == uname) \
                        .one_or_none()

        if not user:
            abort(501, 'Not logged in')

        if not user.blockchain_id_cache:
            root = ET.Element('patient')
            tree = ET.ElementTree(root)
            patient_id = ET.SubElement(root, 'patient_id')
            patient_id.text = str(uuid.uuid4())
            personal = ET.SubElement(root, 'personal_information')
            given, _, family = user.display_name.rpartition(' ')
            name = ET.SubElement(personal, 'name', attrib={'family': family, 'given': given})
            birthdate = ET.SubElement(personal, 'birthdate')
            birthdate.text = '1941-01-08'
            contacts = ET.SubElement(personal, 'contacts')
            email = ET.SubElement(contacts, 'email', attrib={'value': '{}@example.org'.format(user.user_name), 'primary': 'true'})
            phone = ET.SubElement(contacts, 'phone', attrib={'value': '+44 1632 960777'})
            address = ET.SubElement(contacts, 'address')
            address.text = '\n12 Foo Street\nLondon, UK\n'
            billing = ET.SubElement(root, 'billing')
            medical = ET.SubElement(root, 'medical')
            pk, blockchain_id = store_record(ET.tostring(root), b'foobar')
            user.blockchain_id_cache = blockchain_id
            private_key = PrivateKey(user_id=user.id, blockchain_id=blockchain_id, private_key=pk)
            DBSession.add(private_key)
            DBSession.add(user)
        else:
            private_key = DBSession.query(PrivateKey)\
                                   .filter(PrivateKey.blockchain_id == user.blockchain_id_cache)\
                                   .one_or_none()
        user_password_hash = b'foobar'  # this would be the real user's password hash
        record = retrieve_record(user.blockchain_id_cache, private_key.private_key,
                                 user_password_hash)

        edit = False
        if args and args[-1] == 'edit':
            args = args[:-1]
            edit = True

        xpath = '/'.join(('.', ) + args)
        root = ET.fromstring(record)
        node = root.find(xpath)

        name = root.find('name')
        if name:
            name = "{}, {}".format(name.get("family"), name.get("given"))

        if not node:
            abort(404, "xpath: {}".format(xpath))

        if edit:
            return NamespaceEditController(root, xpath, user, record), args

        return NamespaceViewController(node, name), args
