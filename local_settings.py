import os.path
import posixpath
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

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
    
    # Pinax
    
    # project
    'gsm',
]

LANGUAGE_CODE = "fr-FR"
TIME_ZONE = "Europe/Paris"

GSM_USERNAME = 'demo'
GSM_PASSWORD = 'demo'
GSM_LANGUAGE = 'fr'
GSM_URL = 'http://%s:%s@webpull.globalsportsmedia.com' % (
    GSM_USERNAME,
    GSM_PASSWORD,
)
GSM_CACHE = os.path.join(PROJECT_ROOT, 'cache', 'gsm')
