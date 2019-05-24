"""
Django settings for base project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from datetime import timedelta

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# This allow quick development using sqlite
USE_SQLITE = True

# Prefix of your API, e.g /api
API_PREFIX = 'api'

# Path of your API admin, e.g. api_admin
ADMIN_URL = 'api_admin'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Name of application
APP_NAME = 'DRF-Skeleton'

APP_MODULE_BASE = os.path.dirname(os.path.abspath(__file__)).replace(os.getcwd(), '').replace(os.sep, '').strip()

# Auto generated list of application modules
APP_MODULES = [file for file in os.listdir(os.getcwd()) if
               '.' not in file and APP_MODULE_BASE not in file and 'common' and 'appuser' not in file
               and 'templates' not in file and 'administration' not in file] if DEBUG else \
    [file for file in os.listdir(os.getcwd()) if '.' not in file and APP_MODULE_BASE not in file
     and 'test' not in file and 'common' not in file and 'templates' not in file and 'appuser' not in file
     and 'administration' not in file]

# Store classes created by reflection, avoid high overhead by repeated reflection call
CLASS_CACHE = {}

# User settings
AUTH_USER_MODEL = 'appuser.User'

# Pagination Settings
PAGE_SIZE = 10
PAGE_SIZE_QUERY_PARAM = "per_page"
MAX_PAGE_SIZE = 50

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!9ddfwq@1wa5mbyw&%9tvm%p2n+%l_w_5p5y=km$gvevp(-&uk'

ALLOWED_HOSTS = ['localhost']

# This allow frontend and backend to run on different port, turn off in production
CORS_ORIGIN_ALLOW_ALL = True if DEBUG else False

# Application definition
INSTALLED_APPS = [
                     'django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                     'django.contrib.humanize',
                     'rest_framework',
                     'django_filters',
                     'appuser',
                     'administration.apps.AdminConfig',
                 ] + [module for module in APP_MODULES]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.Pager',
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticatedOrReadOnly'
        'rest_framework.permissions.IsAuthenticated'
    ],
    'SEARCH_PARAM': 'q',
}

# JWT token configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

ROOT_URLCONF = f"{APP_MODULE_BASE}.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = f"{APP_MODULE_BASE}.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        } if USE_SQLITE
        else
        {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'monitoring',
            'USER': 'postgres',
            'PASSWORD': 'openkore',
            'HOST': 'localhost',
            'PORT': '5432',
        }
}

# To Show SQL
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join('../', 'static')

# Prevent problem with static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
