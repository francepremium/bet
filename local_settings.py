import os.path
import posixpath
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

gettext = lambda s: s


DATABASES = {
    'default': {
        'ENGINE': 'postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'bet_prod',                       # Or path to database file if using sqlite3.
        'USER': 'bet_prod',                             # Not used with sqlite3.
        'PASSWORD': 'stnuSNE8OUToeuTEUSHNNTtsnhsntoheu987987EUHTD',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}


SENTRY_KEY = 'ENUTntheou)(098eu)(E0U983$@#$@34342oasuth90$#@$#@'
SENTRY_REMOTE_URL = 'http://beta.yourlabs.org/sentry/store/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = "!0!i2uocz=ks1yxvlx*x5o6sn$n_h6a5r5n8@k+qn$d4q+@pnq"

DEBUG=True
TEMPLATE_DEBUG=DEBUG
SERVE_MEDIA=DEBUG

try:
    from personal_settings import *
except ImportError:
    pass
