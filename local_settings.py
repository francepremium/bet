import os.path
import posixpath
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

gettext = lambda s: s


DATABASES = {
    "default": {
        "ENGINE": "postgresql_psycopg2", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "bet.yourlabs.org",                       # Or path to database file if using sqlite3.
        "USER": "bet.yourlabs.org",                             # Not used with sqlite3.
        "PASSWORD": "stnuSNE8OUTNhstnoeuasnt",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

MIDDLEWARE_CLASSES = [
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware'
]


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
    'localeurl',
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.comments",
    
    "pinax.templatetags",
    "emailconfirmation",
    "pinax.apps.account",
    
    # external
    'modeltranslation',
    "staticfiles",
    "debug_toolbar",
    "mailer",
    "uni_form",
    "django_openid",
    "ajax_validation",
    "timezones",
    "emailconfirmation",
    'django_extensions',
    'django_filters',
    'pagination',
    'ajax_select',
    'sentry.client',
    'avatar',
    
    # Pinax
    
    # project
    'gsm',
    'bookmaker',
    'bet',
    'clan',
]

LANGUAGE_CODE = "fr_FR"
TIME_ZONE = "Europe/Paris"
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

SPORTS=(
    ('soccer', 'Soccer'),
    ('tennis', 'Tennis'),
    ('basketball', 'Basketball'),
    ('rugby', 'Rugby'),
)

ACCOUNT_OPEN_SIGNUP = True
LOGIN_URL='/account/login/'

AJAX_LOOKUP_CHANNELS = {
    'session': ('gsm.lookups', 'SessionLookup'),
}

DEBUG=True

SENTRY_KEY = 'ENUTntheou)(098eu)(E0U983$@#$@34342oasuth90$#@$#@'
SENTRY_REMOTE_URL = 'http://beta.yourlabs.org/sentry/store/'

ACCOUNT_EMAIL_VERIFICATION = False
EMAIL_CONFIRMATION_DAYS = 3
