"""
WSGI config for codejam project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import datetime, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codejam.settings")
os.environ['TZ']="Asia/Kolkata"
time.tzset()
application = get_wsgi_application()
