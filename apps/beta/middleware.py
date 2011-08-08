from django import shortcuts
from django.conf import settings
from django.core import urlresolvers

try:
    BETA_URL = urlresolvers.reverse('beta_homepage')
except:
    raise Exception('Please include beta.urls in your urls')

try:
    BYPASS_URLS = settings.BETA_BYPASS_URLS
except:
    BYPASS_URLS = []

BYPASS_URLS.append(BETA_URL)

for test in ['acct_passwd_reset', 'acct_passwd_reset_done', 'acct_passwd_reset_key']:
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
            if BYPASS_URLS[i][0:3] == '/' + code:
                BYPASS_URLS[i] = BYPASS_URLS[i][3:]

class LoginMiddleware(object):
    def process_request(self, request):
        path = request.path_info

        for url in BYPASS_URLS:
            if path.find(url) == 0:
                return None

        if not request.user.is_authenticated():
            return shortcuts.redirect(BETA_URL)
