"""
WSGI config for lunchmanager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Read environment variables from a .env file
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

if os.getenv('PRODUCTION', False) == 'True':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'lunchmanager.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'lunchmanager.settings.local')

application = get_wsgi_application()
