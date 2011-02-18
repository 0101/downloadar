import os
from os.path import abspath, dirname, join
import sys

PROJECT_ROOT = abspath(join(dirname(__file__), '..', 'downloadar'))

sys.path.insert(0, PROJECT_ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()