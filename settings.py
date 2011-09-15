# -*- coding: utf-8 -*-
# https://docs.djangoproject.com/en/dev/ref/settings/

import os

ADMINS = [
    ('James Pic', 'jpic@yourlabs.org'),
    ('James Pic', 'jamespic@gmail.com'),
    ('David Bellaiche', 'contact@betspire.com'),
]
MANAGERS = ADMINS

LANGUAGE_CODE = 'fr_FR'
TIME_ZONE = 'Europe/Paris'

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
    'scoobet.context_processors.inbox_count',
    'gsm.context_processors.available_timezones',
]

MIDDLEWARE_CLASSES = [
    'localeurl.middleware.LocaleURLMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'beta.middleware.LoginMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'gsm.middleware.TimezoneMiddleware',
    'middleware.ExceptionMiddleware',
]

EXCEPTION_MIDDLEWARE_HANDLES = [
    'HtmlInsteadOfXml',
    'ServerOverloaded',
    'MessagingUnauthorizedUser',
]

INSTALLED_APPS = [
    'localeurl',
    'beta',
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
    'staticfiles',
    'debug_toolbar',
    'mailer',
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
    #'devserver',

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

from yourlabs.setup import Setup
setup = Setup(globals())
setup.debug(True)
setup.full() 

if setup.ready:
    setup.add_logger('gsm')
    GSM_CACHE = os.path.join(VAR_ROOT, 'cache', 'gsm')

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
