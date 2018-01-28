# -*- coding: utf-8 -*-
"""Setup the blockmrs application"""
from __future__ import print_function, unicode_literals
import transaction
from blockmrs import model


def bootstrap(command, conf, vars):
    """Place any commands to setup blockmrs here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        # TODO: Set up permissions to model AlgoBOWL permissions, groups correctly
        u = model.User()
        u.user_name = 'jrosenth'
        u.display_name = 'Jack Rosenthal'
        model.DBSession.add(u)

        g = model.Group()
        g.group_name = 'admins'
        g.display_name = 'Admins'
        g.users.append(u)
        model.DBSession.add(g)

        p = model.Permission()
        p.permission_name = 'admin'
        p.description = 'Admin'
        p.groups.append(g)
        model.DBSession.add(p)

        u = model.User()
        u.user_name = 'student'
        u.display_name = 'Default Student'
        model.DBSession.add(u)

        g = model.Group()
        g.group_name = 'students'
        g.display_name = 'Students'
        g.users.append(u)
        model.DBSession.add(g)

        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print('Warning, there was a problem adding your auth data, '
              'it may have already been added:')
        import traceback
        print(traceback.format_exc())
        transaction.abort()
        print('Continuing with bootstrapping...')

    # <websetup.bootstrap.after.auth>
