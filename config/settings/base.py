"""
Django settings for lunchmanager project.

Generated by 'django-admin startproject' using Django 3.1rc1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os
from datetime import time
from pathlib import Path

from django.core.management.utils import get_random_secret_key


BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())

SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_auth_adfs',
    'mozilla_django_oidc',
    'rest_framework',
    'rest_framework.authtoken',
    'constance',
    'constance.backends.database',
    'mathfilters',

    'api.apps.ApiConfig',
    'cafeteria.apps.CafeteriaConfig',
    'menu.apps.MenuConfig',
    'profiles.apps.ProfilesConfig',
    'transactions.apps.TransactionsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'cafeteria.middleware.ClearLimitedItemsCache',
    'mozilla_django_oidc.middleware.SessionRefresh',
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "daily_cache_table",
        "TIMEOUT": None,
    }
}

ROOT_URLCONF = 'config.urls'

# Templates Directory
TEMPLATE_DIR = BASE_DIR / 'templates/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            TEMPLATE_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'django_auth_adfs.backend.AdfsAuthCodeBackend',
    'cafeteria.auth.PowerSchoolGuardianOIDC',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_ADFS = {
    'AUDIENCE': os.getenv('AZURE_APP_ID', ''),
    'CLIENT_ID': os.getenv('AZURE_APP_ID', ''),
    'RELYING_PARTY_ID': os.getenv('AZURE_APP_ID', ''),
    'TENANT_ID': os.getenv('AZURE_TENANT_ID', ''),
    'CLAIM_MAPPING': {
        'first_name': 'given_name',
        'last_name': 'family_name',
        'email': 'upn'
    },
    'CREATE_NEW_USERS': False,
    'GROUP_TO_FLAG_MAPPING': {
        'is_staff': 'Cafeteria',
        'is_superuser': 'IT Department'
    },
}

OIDC_RP_CLIENT_ID = os.getenv('POWERSCHOOL_CLIENT_ID', '')
OIDC_RP_CLIENT_SECRET = os.getenv('POWERSCHOOL_CLIENT_SECRET', '')
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('POWERSCHOOL_URL', '') + 'oauth2/authorize.action'
OIDC_OP_TOKEN_ENDPOINT = os.getenv('POWERSCHOOL_URL', '') + 'oauth2/token.action'
OIDC_OP_USER_ENDPOINT = os.getenv('POWERSCHOOL_URL', '') + 'oauth2/userinfo.action'
OIDC_OP_JWKS_ENDPOINT = os.getenv('POWERSCHOOL_URL', '') + 'ws/unifiedclassroom/jwks'
OIDC_RP_SIGN_ALGO = 'RS512'
OIDC_RP_SCOPES = 'openid email profile'
OIDC_USERNAME_ALGO = 'cafeteria.auth.generate_username'
OIDC_OP_LOGOUT_URL_METHOD = 'cafeteria.auth.powerschool_logout'
# OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 30
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Email settings
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_PORT = os.getenv('EMAIL_PORT', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', '')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

LOGIN_URL = 'django_auth_adfs:login'
LOGIN_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# MEDIA_ROOT = BASE_DIR / 'resources/'
MEDIA_URL = '/resources/'

# Django REST Framework Settings
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Constance Configuration
# https://django-constance.readthedocs.io/en/latest/index.html
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'BALANCE_EXPORT_PATH': ('/', 'File path where current balance export files should be saved.'),
    'CLOSED_FOR_SUMMER': (False, 'The cafeteria is closed for the summer.'),
    'CLOSE_TIME': (time(23, 15), 'The time orders should stop being accepted.', time),
    'CURRENT_YEAR': ('', 'Current school year.'),
    'DEBT_LIMIT': (0.00, 'Debt limit when users are prevented from ordering.'),
    'NEW_CARD_FEE': (0.00, 'Fee charged for a new lunch card.'),
    'OPEN_TIME': (time(0, 0), 'The time orders should start being accepted.', time),
    'REPORTS_EMAIL': ('', 'Email addresses, comma seperated, to which system reports should be sent.'),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'General Settings': ('OPEN_TIME', 'CLOSE_TIME', 'CLOSED_FOR_SUMMER', 'DEBT_LIMIT', 'NEW_CARD_FEE', 'REPORTS_EMAIL', 'BALANCE_EXPORT_PATH', 'CURRENT_YEAR'),
}
