"""Portal controller module"""

from tg import expose, redirect, abort

from blockmrs.lib.base import BaseController
from blockmrs.model import DBSession, User
from blockmrs.lib.renderpr import match_field
from xml.etree import ElementTree as ET

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
        xpath = '/'.join(('.', ) + args)
        tree = ET.parse('data/yacht.xml')
        root = tree.getroot()
        node = root.find(xpath)

        if not node:
            abort(404, "xpath: {}".format(xpath))

        return NamespaceViewController(node), args
