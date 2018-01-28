"""Portal controller module"""

from tg import expose, request, abort, redirect
from xml.etree import ElementTree as ET
import uuid

from blockmrs.lib.base import BaseController
from blockmrs.model import DBSession, User, PrivateKey
from blockmrs.lib.renderpr import match_field
from blockmrs.lib.records import retrieve_record, store_record


__all__ = ['UserPortalController']

class NamespaceViewController(BaseController):
    def __init__(self, nselem):
        self.nselem = nselem

    @expose('blockmrs.templates.portal')
    def _default(self):
        """Handle the user's profile page."""
        return dict(page='profile', view=match_field(self.nselem))


class UserPortalController(BaseController):
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
            email = ET.SubElement(contacts, 'email', attrib={'value': '{}@example.org'.format(user.user_name)})
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

        xpath = '/'.join(('.', ) + args)
        root = ET.fromstring(record)
        node = root.find(xpath)

        if not node:
            abort(404, "xpath: {}".format(xpath))

        return NamespaceViewController(node), args
