# -*- coding: utf-8 -*-
# https://docs.djangoproject.com/en/dev/ref/settings/

import os, os.path, posixpath

ADMINS = [
    ('James Pic', 'jpic@yourlabs.org'),
    ('James Pic', 'jamespic@gmail.com'),
    ('David Bellaiche', 'contact@betspire.com'),
]
MANAGERS = ADMINS

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

MEDIA_ROOT=os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL='/site_media/media/'
STATIC_ROOT=os.path.join(PROJECT_ROOT, 'static')
STATIC_URL='/site_media/static/'
COMPRESS_ROOT=os.path.join(PROJECT_ROOT, 'site_media', 'static')


TEMPLATE_CONTEXT_PROCESSORS = [
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.static',
    #'staticfiles.context_processors.static_url',
    'pinax.core.context_processors.pinax_settings',
    'bet.context_processors.incomplete_ticket',
    'scoobet.context_processors.inbox_count',
    'gsm.context_processors.available_timezones',
    'gsm.context_processors.five_popular_sessions',
    'context_processors.save_user_locale',
]

#gnochi-cms
DEFAULT_TEMPLATE = 'default.html'

MIDDLEWARE_CLASSES = [
    'localeurl.middleware.LocaleURLMiddleware',
    #'johnny.middleware.LocalStoreClearMiddleware',
    #'johnny.middleware.QueryCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'beta.middleware.LoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'gsm.middleware.TimezoneMiddleware',
    'middleware.ExceptionMiddleware',
]

APPEND_SLASH = True

EXCEPTION_MIDDLEWARE_HANDLES = [
    'HtmlInsteadOfXml',
    'ServerOverloaded',
    'MessagingUnauthorizedUser',
    'BetTooLateException',
]

INSTALLED_APPS = [
    'localeurl',
    'beta',
    'compressor',
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.comments',
    'django.contrib.markup',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    
    'pinax.templatetags',
    'emailconfirmation',
    'pinax.apps.account',
    
    # external
    #'staticfiles',
    'debug_toolbar',
    #'mailer',
    'uni_form',
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
    'taggit',
    'subscription',
    'subscription.examples.yourlabs',
    #'devserver',

    'rosetta',
    # Pinax
   
    # to open source
    'clan',
    'article',
    'yourlabs.smoke',
    'yourlabs.runner',

    # project
    'gsm',
    'bookmaker',
    'bet',


    # this must be at the end because it monkey patches the admin
    'scoobet',
    'haystack',
    'modeltranslation',
]

ROSETTA_MESSAGES_PER_PAGE=100
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS=True
BING_APP_ID='3AF372499E210397A857F17733E469F3323B164C'

SUBSCRIPTION_NOTIFICATION_QUEUES = [
    'chat',
    'friends',
]

COMPRESS_ENABLED=True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

ACCOUNT_EMAIL_VERIFICATION = True

SMOKE_TEST_USERNAME='gsm_test'
SMOKE_TEST_PASSWORD='()&*EUTOSHue()&*UESTNHlrch'

GSM_LOCKFILE_POLLRATE = .1
GSM_LOCKFILE_MAXPOLLS = 30
GSM_USERNAME = 'betspire'
GSM_PASSWORD = 'lixzw2c'
GSM_LANGUAGE = 'fr'
GSM_URL = 'http://%s:%s@webpull.globalsportsmedia.com' % (
    GSM_USERNAME,
    GSM_PASSWORD,
)
# for upstream server overload test
#GSM_URL = 'http://localhost:8000'

# we have our own locale switcher
LOCALEURL_USE_ACCEPT_LANGUAGE = False

import re
LOCALE_INDEPENDENT_PATHS = [
    re.compile('/notifications/json/'),
    re.compile('/notifications/push/'),
]

gettext = lambda x: x
LANGUAGES = (
    ('en', gettext('English')),
    ('fr', gettext('French')),
)

USE_PINAX = True

AJAX_LOOKUP_CHANNELS = {
    'session': ('gsm.lookups', 'SessionLookup'),
    'user': {'model': 'auth.User', 'search_field':'username'},
}

USE_COMMENTS_AS_WALL = True

HAYSTACK_ENABLE_REGISTRATION = False

SUBSCRIPTION_BACKENDS = {
    'storage': 'subscription.examples.yourlabs.backends.RedisBackend',
}

CACHES = {
    'default' : dict(
        BACKEND = 'johnny.backends.memcached.MemcachedCache',
        LOCATION = ['127.0.0.1:11211'],
        JOHNNY_CACHE = True,
    )
}
JOHNNY_MIDDLEWARE_KEY_PREFIX='bet'

from yourlabs.setup import Setup
setup = Setup(globals())
setup.debug(False)
setup.full() 

if setup.ready:
    setup.add_logger('redis')
    setup.add_logger('gsm')
    setup.add_logger('gsm_bugs')
    setup.add_logger('gsm_delete')
    GSM_CACHE = os.path.join(VAR_ROOT, 'cache', 'gsm')

    if not os.path.exists(GSM_CACHE):
        os.makedirs(GSM_CACHE)

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
from local_settings import *
