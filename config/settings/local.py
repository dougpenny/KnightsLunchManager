from .base import *


ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {'level': 'INFO', 'handlers': ['console']},
    'formatters': {
        'app': {
            'format': (
                u'%(asctime)s [%(levelname)-8s] '
                '(%(module)s.%(funcName)s) %(message)s'
            ),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'app'
        },
    },
    'loggers': {
        'django_auth_adfs': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'mozilla_django_oidc': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    },
}
