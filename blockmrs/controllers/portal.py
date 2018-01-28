"""Portal controller module"""

from tg import expose, request, abort, redirect, predicates
from xml.etree import ElementTree as ET

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
            redirect('/p/edit')

        private_key = DBSession.query(PrivateKey) \
                               .filter(PrivateKey.blockchain_id == user.blockchain_id_cache) \
                               .one_or_none()
        user_password_hash = b'foobar'  # this would be the real user's password hash
        record = retrieve_record(user.blockchain_id_cache, private_key,
                                 user_password_hash)

        xpath = '/'.join(('.', ) + args)
        tree = ET.fromstring(record)
        root = tree.getroot()
        node = root.find(xpath)

        if not node:
            abort(404, "xpath: {}".format(xpath))

        return NamespaceViewController(node), args
