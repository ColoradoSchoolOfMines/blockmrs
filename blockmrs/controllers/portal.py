"""Portal controller module"""

from tg import expose, redirect, abort

from depot.manager import DepotManager

from blockmrs.lib.base import BaseController
from blockmrs.model import DBSession, User

__all__ = ['UserPortalController']


class PortalController(BaseController):
    def __init__(self, user):
        self.user = user

    @expose('blockmrs.templates.portal')
    def _default(self):
        """Handle the user's profile page."""
        return dict(page='profile', u=self.user)

    @expose()
    def picture(self):
        """Return the user's profile picture."""
        if self.user.profile_pic:
            redirect(DepotManager.url_for(self.user.profile_pic.path))
        else:
            redirect('/img/default_profile_pic.jpg')


class UserPortalController(BaseController):
    @expose()
    def _lookup(self, uname, *args):
        user = DBSession.query(User) \
                        .filter(User.user_name == uname) \
                        .one_or_none()
        if not user:
            abort(404, "No such user")

        return PortalController(user), args
