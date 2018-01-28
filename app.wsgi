# This file could be used to deploy the site in production, assuming
# that your configuration is at "production.ini"

import os
PASTE_CONFIG = os.getcwd() + '/production.ini'

import logging.config
logging.config.fileConfig(PASTE_CONFIG)

from paste.deploy import loadapp
application = loadapp('config:{}'.format(PASTE_CONFIG))
