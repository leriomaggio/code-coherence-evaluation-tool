"""
Django settings for comments_classification project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# --------------------------------------------------------------------------
# NOTE: COMMENT THIS in case of importing settings from NOTEBOOK or Scripts
# --------------------------------------------------------------------------

# importing django-celery
#import djcelery
#djcelery.setup_loader()  # Set settings of Django Celery

# --------------------------------------------------------------------------

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v&l1g6zm_1n(qf_1zj*tv4c^n=76nuz6n^k)q_qhs*-=bw1lk-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Custom Apps
    'source_code_analysis',
    'agreement_evaluations',
    'djcelery',                 # Add Django Celery
    # This would add support for the django:// broker.
    # So far we're going to use the default RabbitMQ broker
    # 'kombu.transport.django',
    'coherence_dataset',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Added this to enable Language Switching
)

ROOT_URLCONF = 'comments_classification.urls'

WSGI_APPLICATION = 'comments_classification.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'code_comments_evaluation',
        'USER': 'cc_evaluator',
        'PASSWORD': 'cc_evaluator',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

from django.utils.translation import ugettext_lazy as _

LANGUAGES = (
    ('en-us', _('English')),
    ('it', _('Italian')),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "source_code_analysis/resources"),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
    os.path.join(BASE_DIR, "source_code_analysis", "templates"),
)

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# SESSIONS settings customization
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# SESSION_COOKIE_AGE = 10 #(5*60)  # 5 minutes in seconds

# Django-Celery Settings
BROKER_URL = 'amqp://valerio:me@rabbitmq@localhost:5672/osx_host'
# BROKER_URL = 'django://'

CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'

# Celeryd Settings that are ready for Production

# Name of nodes to start
# here we have a single node
CELERYD_NODES="w1"

# Absolute path to "manage.py"
CELERY_BIN=os.path.abspath(os.path.join(BASE_DIR, "../", "manage.py"))

# How to call manage.py
CELERYD_MULTI="celery multi"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# %N will be replaced with the first part of the nodename.
CELERYD_PID_FILE="/var/run/celery/%N.pid"
