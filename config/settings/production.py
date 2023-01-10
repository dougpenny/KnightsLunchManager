from .base import *

import os
import sys


ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

if len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv('POSTGRES_HOST') is None:
        raise Exception('POSTGRES_HOST environment variable not defined')
    if os.getenv('POSTGRES_NAME') is None:
        raise Exception('POSTGRES_NAME environment variable not defined')
    if os.getenv('POSTGRES_USER') is None:
        raise Exception('POSTGRES_USER environment variable not defined')
    if os.getenv('POSTGRES_PASSWORD') is None:
        raise Exception('POSTGRES_PASSWORD environment variable not defined')
    if os.getenv('POSTGRES_PORT') is None:
        raise Exception('POSTGRES_PORT environment variable not defined')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_NAME'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': os.getenv('POSTGRES_HOST'),
            'PORT': os.getenv('POSTGRES_PORT'),
        }
    }

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {'level': 'INFO', 'handlers': ['file']},
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'app',
            'filename': os.getenv('LOG_PATH', ''),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
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
