from .base import *

import logging.config


ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': '5432',
    }
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# setup Django to log to a file
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {'level': 'INFO', 'handlers': ['file']},
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/lunchmanager/django.log',
            'formatter': 'app',
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
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
}
