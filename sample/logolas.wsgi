"""Sample WSGI file for Logolas."""

# Apache Configuration
#WSGIDaemonProcess logolas user=www-data group=www-data threads=2 python-path=/path/to/logolas/venv/lib/python2.7/site-packages
#WSGIScriptAlias /admin/logolas /path/to/logolas/logolas.wsgi

#<Directory /path/to/logolas/logolas/>
#        WSGIProcessGroup logolas
#        WSGIApplicationGroup %{GLOBAL}
#</Directory>

import sys

sys.path.insert(0, '/path/to/logolas/')

activate_this = '/path/to/logolas/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from logolas.configuration import Configuration
from logolas.web.app import application as app_factory

config = Configuration()
config.load_yaml('/path/to/logolas/config.yml')

application = app_factory(config)
