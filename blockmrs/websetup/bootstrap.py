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
        u1 = model.User()
        u1.user_name = 'jrosenth'
        u1.display_name = 'Jack Rosenthal'
        model.DBSession.add(u1)

        u2 = model.User()
        u2.user_name = 'david'
        u2.display_name = 'David Florness'
        model.DBSession.add(u2)

        u3 = model.User()
        u3.user_name = 'sumner'
        u3.display_name = 'Sumner Evans'
        model.DBSession.add(u3)

        u4 = model.User()
        u4.user_name = 'robby'
        u4.display_name = 'Robby Zampino'
        model.DBSession.add(u4)

        g = model.Group()
        g.group_name = 'admins'
        g.display_name = 'Admins'
        g.users += [u1, u2, u3, u4]
        model.DBSession.add(g)

        p = model.Permission()
        p.permission_name = 'admin'
        p.description = 'Admin'
        p.groups.append(g)
        model.DBSession.add(p)

        u5 = model.User()
        u5.user_name = 'raymond'
        u5.display_name = 'Raymond Luxury Yacht'
        model.DBSession.add(u5)

        g = model.Group()
        g.group_name = 'patients'
        g.display_name = 'Patients'
        g.users.append(u5)
        model.DBSession.add(g)

        u6 = model.User()
        u6.user_name = 'graham'
        u6.display_name = 'Graham Chapman'
        model.DBSession.add(u6)

        g = model.Group()
        g.group_name = 'doctor'
        g.display_name = 'Doctors'
        g.users.append(u6)
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
