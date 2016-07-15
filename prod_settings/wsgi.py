"""
WSGI config for rampup project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
import datetime, time

sys.path.append('/nobackup/paramp/django/sw/packages/python/current/lib/python2.7/site-packages')
sys.path.append('/var/lib/jenkins/workspace/CodeJam/')
sys.path.append('/var/lib/jenkins/workspace/CodeJam/codejam/')

os.environ["DJANGO_SETTINGS_MODULE"] = "codejam.settings"

os.environ['TZ']="Asia/Kolkata"
time.tzset()

application = get_wsgi_application()
