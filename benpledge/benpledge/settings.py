"""
Django settings for benpledge project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0eu763+(x*w0i)%zx1x$7d0fs5ce*!#fjm=ux+q8v+)=k+u%my'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['95.85.39.60']


# Application definition

INSTALLED_APPS = (
    # django default applications
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # third party applications
    'south',
    'registration',
    'bootstrap3',
    'widget_tweaks',
    'contact_form',
    # local applications
    'publicweb',
)

ACCOUNT_ACTIVATION_DAYS = 7
SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR +'/emails/' 

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.request',
)

ROOT_URLCONF = 'benpledge.urls'

WSGI_APPLICATION = 'benpledge.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS' : {
            'read_default_file': '/opt/benpledge/dbconfig.cnf',
        },
    }
}

ADMINS = (
    ('Philip McMahon', '13phil13+benpledgeerr@gmail.com'),
)

MANAGERS = (
    ('Philip McMahon', '13phil13+benpledgelink@gmail.com'),
    ('p2', '13phil13@gmail.com')
)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'GMT'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = '/opt/benpledge/static/'
STATIC_URL = '/static/'

LOGIN_URL = '/accounts/login'

MEDIA_ROOT = BASE_DIR + '/publicweb/media/'
MEDIA_URL = BASE_DIR + '/publicweb/media/'

# Email settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'benpledgehelp'
EMAIL_HOST_PASSWORD = 'retrofit123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = 'benpledge - '

try:
    from local_settings import *
except ImportError:
    print "local settings not found"
    pass