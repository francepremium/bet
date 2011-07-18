import os.path
import posixpath
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

gettext = lambda s: s


DATABASES = {
    'default': {
        'ENGINE': 'postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bet.yourlabs.org',                       # Or path to database file if using sqlite3.
        'USER': 'bet.yourlabs.org',                             # Not used with sqlite3.
        'PASSWORD': 'stnuSNE8OUTNhstnoeuasnt',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}


DEBUG=True

SENTRY_KEY = 'ENUTntheou)(098eu)(E0U983$@#$@34342oasuth90$#@$#@'
SENTRY_REMOTE_URL = 'http://beta.yourlabs.org/sentry/store/'

try:
    from personal_settings import *
except ImportError:
    pass
