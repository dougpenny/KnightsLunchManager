from .base import *

import os
import sys

from logtail import LogtailHandler

import dj_database_url


ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

if len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv('DATABASE_URL', None) is None:
        raise Exception('DATABASE_URL environment variable not defined')
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL')),
    }

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {'level': 'INFO', 'handlers': ['logtail']},
    'handlers': {
        'logtail': {
            'class': 'logtail.LogtailHandler',
            'formatter': 'app',
            'source_token': os.getenv('LOGTAIL_SOURCE_TOKEN', '')
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logtail'],
            'level': 'INFO',
            'propagate': True
        },
    },
    'formatters': {
        'app': {
            'format': '{name} at {asctime} ({levelname}) :: {message}',
            'style': '{'
        },
    },
}
