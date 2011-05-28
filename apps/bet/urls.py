from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('bet.views',
    url(
        r'(?P<bet_pk>[^/]+)/pronostic/form/$',
        'pronostic_form', {
        }, 'bet_pronostic_form'
    ),
    url(
        r'add/$',
        'add', {
        }, 'bet_add'
    ),
)
