# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in acm-website.

This file complements development/deployment.ini.

"""
from tg.configuration import AppConfig

import blockmrs
import transaction
import tg.predicates
from blockmrs import model, lib
from blockmrs.model.auth import User
from tg import request
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig

# Depot
from depot.manager import DepotManager

base_config = AppConfig()
base_config.renderers = []

# True to prevent dispatcher from striping extensions
# For example /socket.io would be served by "socket_io"
# method instead of "socket".
base_config.disable_request_extensions = False

# Set None to disable escaping punctuation characters to "_"
# when dispatching methods.
# Set to a function to provide custom escaping.
base_config.dispatch_path_translator = True

base_config.prefer_toscawidgets2 = True

base_config.package = blockmrs

# Enable json in expose
base_config.renderers.append('json')

# Set the default renderer
base_config.renderers.append('kajiki')
base_config['templating.kajiki.strip_text'] = False  # Change this in setup.py too for i18n to work.

base_config.default_renderer = 'kajiki'

# Configure Sessions, store data as JSON to avoid pickle security issues
base_config['session.enabled'] = True
base_config['session.data_serializer'] = 'json'
# Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = blockmrs.model
base_config.DBSession = blockmrs.model.DBSession
# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
# YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
base_config.sa_auth.cookie_secret = "2a654f87-1cb4-43fb-834b-413c449a71a8"
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User

from tg.configuration.auth import TGAuthMetadata

# This tells to TurboGears how to retrieve the data for your user
class ApplicationAuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth):
        self.sa_auth = sa_auth

    def authenticate(self, environ, identity):
        login = identity['login']
        user = self.sa_auth.dbsession.query(self.sa_auth.user_class).filter_by(
            user_name=login
        ).first()

        if not user:
            # Was it a valid MultiPass login? If so, register an account.
            # if auth(login, identity['password']):
            #     info = uidinfo(login)
            #     user = User(
            #        id=info["uidNumber"],
            #        user_name=login,
            #       display_name="{} {}".format(info["first"], info["sn"]))
            #    self.sa_auth.dbsession.add(user)
            #   self.sa_auth.dbsession.flush()
            #    transaction.commit()
            #else:
            login = None
        elif not user.validate_password(identity['password']):
            login = None

        if login is None:
            try:
                from urllib.parse import parse_qs, urlencode
            except ImportError:
                from urlparse import parse_qs
                from urllib import urlencode
            from tg.exceptions import HTTPFound

            params = parse_qs(environ['QUERY_STRING'])
            params.pop('password', None)  # Remove password in case it was there
            if user is None:
                params['failure'] = 'user-not-found'
            else:
                params['login'] = identity['login']
                params['failure'] = 'invalid-password'

            # When authentication fails send user to login page.
            environ['repoze.who.application'] = HTTPFound(
                location=environ['SCRIPT_NAME'] + '?'.join(('/login', urlencode(params, True)))
            )

        return login

    def get_user(self, identity, userid):
        return self.sa_auth.dbsession.query(self.sa_auth.user_class).filter_by(
            user_name=userid
        ).first()

    def get_groups(self, identity, userid):
        return [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return [p.permission_name for p in identity['user'].permissions]

base_config.sa_auth.dbsession = model.DBSession

base_config.sa_auth.authmetadata = ApplicationAuthMetadata(base_config.sa_auth)

# In case ApplicationAuthMetadata didn't find the user discard the whole identity.
# This might happen if logged-in users are deleted.
base_config['identity.allow_missing_user'] = False

# You can use a different repoze.who Authenticator if you want to
# change the way users can login
# base_config.sa_auth.authenticators = [('myauth', SomeAuthenticator()]

# You can add more repoze.who metadata providers to fetch
# user metadata.
# Remember to set base_config.sa_auth.authmetadata to None
# to disable authmetadata and use only your own metadata providers
# base_config.sa_auth.mdproviders = [('myprovider', SomeMDProvider()]

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'

base_config.sa_auth.translations = {
    "user_id": "id",
    "group_id": "id",
    "permission_id": "id",
}

# Admin configuration
class AdminConfig(TGAdminConfig):
    allow_only = tg.predicates.has_permission('admin')


base_config['depot.storage_path'] = "/tmp/depot"

# Configure default depot
tg.milestones.config_ready.register(
    lambda: DepotManager.configure('default', tg.config)
)

# Variable provider: this provides a default set of variables to the templating engine
def variable_provider():
    d = {}
    if request.identity:
        d['luser'] = request.identity['user']
    else:
        d['luser'] = None
    return d

base_config.variable_provider = variable_provider

# Task secheduler
def start_tgscheduler():
    import tgscheduler
    tgscheduler.start_scheduler()

    # TODO: Schedule some tasks here Jack

from tg.configuration import milestones
milestones.config_ready.register(start_tgscheduler)

try:
    # Enable DebugBar if available, install tgext.debugbar to turn it on
    from tgext.debugbar import enable_debugbar
    enable_debugbar(base_config)
except ImportError:
    pass
