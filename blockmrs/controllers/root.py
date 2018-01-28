from tg import expose, flash, require, url, lurl, config
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.exceptions import HTTPFound
from tg import predicates
from blockmrs import model
from blockmrs.model import DBSession
from blockmrs.config.app_cfg import AdminConfig
from tgext.admin.controller import AdminController

from blockmrs.lib.base import BaseController
from blockmrs.controllers.error import ErrorController
from blockmrs.controllers.portal import UserPortalController

__all__ = ['RootController']

class RootController(BaseController):
    admin = AdminController(model, DBSession, config_type=AdminConfig, translations=config.sa_auth.translations)
    error = ErrorController()
    p = UserPortalController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "BlockMRS"

    @expose('blockmrs.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('blockmrs.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('blockmrs.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('blockmrs.templates.login')
    def login(self, came_from=lurl('/portal'), failure=None, login='', signup=False):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login',
                    login_counter=str(login_counter),
                    came_from=came_from,
                    signup=signup,
                    login=login)

    @expose()
    def post_login(self, came_from=lurl('/portal')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        print(came_from)
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)

    @expose()
    def portal(self):
        """Redirect the user to their portal."""
        userid = request.identity['repoze.who.userid']
        return HTTPFound(location=lurl('/p/{}'.format(userid)))
