# -*- coding: utf-8 -*-
# Django settings for main project.

import os.path
import posixpath
import pinax

gettext = lambda s: s
PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = "default"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

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

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "US/Eastern"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "media"),
    os.path.join(PINAX_ROOT, "media", PINAX_THEME),
]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = "!0!i2uocz=ks1yxvlx*x5o6sn$n_h6a5r5n8@k+qn$d4q+@pnq"

# List of callables that know how to import templates from various sources.
#TEMPLATE_LOADERS = [
    #'django.template.loaders.filesystem.Loader',
    #'django.template.loaders.app_directories.Loader',
#]


ROOT_URLCONF = "urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
]

#TEMPLATE_STRING_IF_INVALID = '[INVALID VARIABLE: {{ %s }}]'

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    
    "staticfiles.context_processors.static_url",
    
    "pinax.core.context_processors.pinax_settings",
]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    
    "pinax.templatetags",
    
    # external
    "staticfiles",
    "debug_toolbar",
    
    # Pinax
    
    # project
]

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}



MIDDLEWARE_CLASSES = [
    'middleware.ProfilerMiddleware',
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
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
    # 'postman',
    'south',
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

GSM_USERNAME = 'cportal'
GSM_PASSWORD = 'client'
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

POSTMAN_DISALLOW_ANONYMOUS=True
POSTMAN_DISALLOW_MULTIRECIPIENTS=True
POSTMAN_DISALLOW_COPIES_ON_REPLY=False
POSTMAN_AUTO_MODERATE_AS=True
POSTMAN_AUTOCOMPLETER_APP={
    'arg_default': 'user',
}

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

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
