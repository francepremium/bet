from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('bet.views',
    url(
        r'(?P<bet_pk>[0-9]+)/pronostic/add/$',
        'add_pronostic', {
        }, 'bet_add_pronostic'
    ),
    url(
        r'add/$',
        'add', {
        }, 'bet_add'
    ),
)
