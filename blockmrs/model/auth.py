import os
from datetime import datetime, time
__all__ = ['User', 'Group', 'Permission']

from sqlalchemy import Table, ForeignKey, Column, Binary
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean, Numeric
from sqlalchemy.orm import relation
from blockmrs.model import DeclarativeBase, metadata, DBSession

group_permission_table = Table('groups_permissions_xref', metadata,
                               Column('group_id', Integer,
                                      ForeignKey('groups.id',
                                                 onupdate="CASCADE",
                                                 ondelete="CASCADE"),
                                      primary_key=True),
                               Column('permission_id', Integer,
                                      ForeignKey('permissions.id',
                                                 onupdate="CASCADE",
                                                 ondelete="CASCADE"),
                                      primary_key=True))


user_group_table = Table('users_groups_xref', metadata,
                         Column('user_id', Integer,
                                ForeignKey('users.id',
                                           onupdate="CASCADE",
                                           ondelete="CASCADE"),
                                primary_key=True),
                         Column('group_id', Integer,
                                ForeignKey('groups.id',
                                           onupdate="CASCADE",
                                           ondelete="CASCADE"),
                                primary_key=True))

class Group(DeclarativeBase):
    __tablename__ = 'groups'

    id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)
    users = relation('User', secondary=user_group_table, backref='groups')

    def __repr__(self):
        return 'Group("{}")'.format(self.group_name)

    def __str__(self):
        return self.group_name


class PrivateKey(DeclarativeBase):
    __tablename__ = 'privatekeys'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    blockchain_id = Column(Integer, nullable=False)
    private_key = Column(Binary, nullable=False)


class User(DeclarativeBase):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)
    blockchain_id_cache = Column(Integer)
    private_keys = relation('PrivateKey')

    def __repr__(self):
        return 'User("{}")'.format(self.user_name)

    def __str__(self):
        return self.display_name or self.user_name

    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    @classmethod
    def by_user_name(cls, username):
        """Return the user object whose user name is ``username``."""
        return DBSession.query(cls).filter_by(user_name=username).first()

    def validate_password(self, password):
        return True

class Permission(DeclarativeBase):
    __tablename__ = 'permissions'

    id = Column(Integer, autoincrement=True, primary_key=True)
    permission_name = Column(Unicode(63), unique=True, nullable=False)
    description = Column(Unicode(255))

    groups = relation(Group, secondary=group_permission_table,
                      backref='permissions')

    def __repr__(self):
        return 'Permission("{}")'.format(self.permission_name)

    def __str__(self):
        return self.permission_name

