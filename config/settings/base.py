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

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',

    'django_auth_adfs',
    'rest_framework',
    'constance',
    'constance.backends.database',

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
]

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
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_ADFS = {
    'AUDIENCE': os.getenv('ADFS_AUDIENCE'),
    'CLIENT_ID': os.getenv('ADFS_CLIENT_ID'),
    'RELYING_PARTY_ID': os.getenv('ADFS_RELYING_PARTY_ID'),
    'TENANT_ID': os.getenv('ADFS_TENANT_ID'),
    'CLAIM_MAPPING': {
        'first_name': 'given_name',
        'last_name': 'family_name',
        'email': 'upn'
    },
    'GROUP_TO_FLAG_MAPPING': {
        'is_staff': 'Cafeteria',
        'is_superuser': 'IT Department'
    },
}

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

# STATIC_ROOT = BASE_DIR / 'static/'
STATIC_URL = '/static/'

# MEDIA_ROOT = BASE_DIR / 'resources/'
MEDIA_URL = '/resources/'


# Constance Configuration
# https://django-constance.readthedocs.io/en/latest/index.html

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'OPEN_TIME': (time(0,0), 'The time orders should start being accepted.', time),
    'CLOSE_TIME': (time(23,15), 'The time orders should stop being accepted.', time),
    'BALANCE_EXPORT_PATH': ('/', 'File path where current balance export files should be saved.'),
    'POWERSCHOOL_URL': ('', 'Full URL for your PowerSchool server.'),
    'POWERSCHOOL_ID': ('', 'Found in the plugin on your PowerSchool server.'),
    'POWERSCHOOL_SECRET': ('', 'Found in the plugin on your PowerSchool server.'),
    'AZURE_TENANT_ID': ('', 'Found in the Azure portal.'),
    'AZURE_APP_ID': ('', 'Found in the Azure portal.'),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'General Settings': ('OPEN_TIME', 'CLOSE_TIME', 'BALANCE_EXPORT_PATH'),
    'PowerSchool Settings': ('POWERSCHOOL_URL', 'POWERSCHOOL_ID', 'POWERSCHOOL_SECRET'),
    'Azure Settings': ('AZURE_TENANT_ID', 'AZURE_APP_ID'),
}