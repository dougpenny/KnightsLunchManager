from .base import *

import os
import sys

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

# setup Django to log to a file
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'root': {'level': 'INFO', 'handlers': ['file']},
#     'handlers': {
#         'file': {
#             'level': 'INFO',
#             'class': 'logging.FileHandler',
#             'filename': '/var/log/lunchmanager/django.log',
#             'formatter': 'app',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file'],
#             'level': 'INFO',
#             'propagate': True
#         },
#     },
#     'formatters': {
#         'app': {
#             'format': (
#                 u'%(asctime)s [%(levelname)-8s] '
#                 '(%(module)s.%(funcName)s) %(message)s'
#             ),
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#     },
# }
