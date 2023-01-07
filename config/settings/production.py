from .base import *

import os
import sys

import dj_database_url


ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

if len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv('DATABASE_URL') is None:
        raise Exception('DATABASE_URL environment variable not defined')
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL')),
    }

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {'level': 'INFO', 'handlers': ['papertrail']},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'app'
        },
        'papertrail': {
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'app',
            'address': (os.getenv('LOGGING_URL', ''), int(os.getenv('LOGGING_PORT', '')))
        },
    },
    'loggers': {
        'django': {
            'handlers': ['papertrail'],
            'level': 'INFO',
            'propagate': True
        },
    },
    'formatters': {
        'app': {
            'format': (
                u'%(asctime)s [%(levelname)-8s] '
                '(%(module)s.%(funcName)s) %(message)s'
            ),
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
}
