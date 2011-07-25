# -*- coding: utf-8 -*-
# https://docs.djangoproject.com/en/dev/ref/settings/

import os.path
import posixpath
import pinax

gettext = lambda s: s
PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/static/"

PINAX_THEME = "default"
# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "media"),
    os.path.join(PINAX_ROOT, "media", PINAX_THEME),
]
TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
]

# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")
ROOT_URLCONF = "urls"

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SERVE_MEDIA = DEBUG
#TEMPLATE_STRING_IF_INVALID = '[INVALID VARIABLE: {{ %s }}]'

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]
MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "dev.db",                       # Or path to database file if using sqlite3.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

SITE_ID = 1
USE_I18N = True

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

MIDDLEWARE_CLASSES = [
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'pagination.middleware.PaginationMiddleware'
]


TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'staticfiles.context_processors.static_url',
    'pinax.core.context_processors.pinax_settings',
    'bet.context_processors.incomplete_ticket',
]

INSTALLED_APPS = [
    'localeurl',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.comments',
    
    'pinax.templatetags',
    'emailconfirmation',
    'pinax.apps.account',
    
    # external
    'modeltranslation',
    'staticfiles',
    'debug_toolbar',
    'mailer',
    'uni_form',
    'django_openid',
    'ajax_validation',
    'timezones',
    'emailconfirmation',
    'django_extensions',
    'django_filters',
    'pagination',
    'ajax_select',
    'sentry.client',
    'avatar',
    'actstream',
    'endless_pagination',
    'autofixture',
    'nashvegas',
    'django_messages',
    #'devserver',

    # Pinax
    
    # project
    'gsm',
    'bookmaker',
    'bet',
    'clan',
    'scoobet',
    'article',
]

LANGUAGE_CODE = 'fr_FR'
TIME_ZONE = 'Europe/Paris'
LANGUAGES = (
    ('en', gettext('English')),
    ('fr', gettext('French')),
)
MODELTRANSLATION_DEFAULT_LANGUAGE='fr'
MODELTRANSLATION_TRANSLATION_REGISTRY='translation'

GSM_USERNAME = 'betspire'
GSM_PASSWORD = 'lixzw2c'
GSM_LANGUAGE = 'fr'
GSM_URL = 'http://%s:%s@webpull.globalsportsmedia.com' % (
    GSM_USERNAME,
    GSM_PASSWORD,
)
GSM_CACHE = os.path.join(PROJECT_ROOT, 'cache', 'gsm')

ACCOUNT_OPEN_SIGNUP = True
LOGIN_URL='/account/login/'

AJAX_LOOKUP_CHANNELS = {
    'session': ('gsm.lookups', 'SessionLookup'),
    'user': {'model': 'auth.User', 'search_field':'username'},
}

ACCOUNT_EMAIL_VERIFICATION = False
EMAIL_CONFIRMATION_DAYS = 3

DEVSERVER_MODULES = (
    #'devserver.modules.sql.SQLRealTimeModule',
    #'devserver.modules.sql.SQLSummaryModule',
    'devserver.modules.profile.ProfileSummaryModule',

    # Modules not enabled by default
    #'devserver.modules.ajax.AjaxDumpModule',
    # commented out because it cases an exception: MemoryUseModule object has
    # not attribute heapy
    #'devserver.modules.profile.MemoryUseModule',
    'devserver.modules.cache.CacheSummaryModule',
    'devserver.modules.profile.LineProfilerModule',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
}

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
