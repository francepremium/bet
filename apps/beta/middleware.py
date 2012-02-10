from django import shortcuts
from django.conf import settings
from django.core import urlresolvers

try:
    from localeurl.templatetags.localeurl_tags import rmlocale
except ImportError:
    rmlocale = lambda x: x

try:
    BYPASS_URLS = settings.BETA_BYPASS_URLS
except:
    BYPASS_URLS = []

for test in ['acct_passwd_reset', 'acct_passwd_reset_done', 'acct_passwd_reset_key', 'acct_signup']:
    try:
        BYPASS_URLS.append(urlresolvers.reverse(test))
    except:
        pass

for test in ['STATIC_URL', 'MEDIA_URL', 'LOGIN_URL']:
    try:
        BYPASS_URLS.append(getattr(settings, test))
    except:
        pass

if 'localeurl.middleware.LocaleURLMiddleware' in settings.MIDDLEWARE_CLASSES:
    for code, label in settings.LANGUAGES:
        for i in range(0, len(BYPASS_URLS)):
            BYPASS_URLS[i] = rmlocale(BYPASS_URLS[i])

class LoginMiddleware(object):
    def process_request(self, request):
        path = request.path_info
        BETA_URL = rmlocale(urlresolvers.reverse('beta_homepage'))
        if not BETA_URL in BYPASS_URLS:
            BYPASS_URLS.append(BETA_URL)

        if '/account/' in request.path:
            return None
    
        for url in BYPASS_URLS:
            if path.find(url) == 0:
                return None

        if not request.user.is_authenticated():
            return shortcuts.redirect(BETA_URL + '?next=' + request.path)
