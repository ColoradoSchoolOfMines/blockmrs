# -*- coding: utf-8 -*-

#  Quickstarted Options:
#
#  sqlalchemy: True
#  auth:       sqlalchemy
#  mako:       False
#
#

import logging
import multiprocessing
import sys
py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs = [
    'WebTest >= 1.2.3',
    'nose',
    'coverage',
    'gearbox'
]

install_requires = [
    "TurboGears2 >= 2.3.10",
    "Beaker >= 1.8.0",
    "Kajiki >= 0.6.1",
    "zope.sqlalchemy >= 0.4",
    "sqlalchemy",
    "alembic",
    "repoze.who",
    "tw2.forms",
    "tgext.admin >= 0.6.1",
    "WebHelpers2",
    "Babel",
    "filedepot",
    "tgscheduler",
    "ipfsapi",
]

setup(
    name='blockmrs',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'blockmrs': [
        'i18n/*/LC_MESSAGES/*.mo',
        'templates/*/*',
        'public/*/*'
    ]},
    message_extractors={'blockmrs': [
        ('**.py', 'python', None),
        ('templates/**.xhtml', 'kajiki', {'strip_text': False}),
        ('public/**', 'ignore', None)
    ]},
    entry_points={
        'paste.app_factory': [
            'main = blockmrs.config.middleware:make_app'
        ],
        'gearbox.plugins': [
            'turbogears-devtools = tg.devtools'
        ]
    },
    zip_safe=False
)
