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
    'django_extensions',
    'modeltranslation',
    
    # Pinax
    
    # project
    'gsm',
]

LANGUAGE_CODE = "fr-FR"
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
