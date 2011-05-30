from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('bet.views',
    url(
        r'ticket/(?P<ticket_pk>[^/]+)/delete/$',
        'ticket_delete', {
        }, 'bet_ticket_delete'
    ),
    url(
        r'ticket/add/$',
        'ticket_add', {
        }, 'bet_ticket_add'
    ),
    url(
        '(?P<bet_pk>[0-9]+)/delete/$',
        'bet_delete', {
        }, 'bet_delete'
    ),
    url(
        r'(?P<ticket_pk>[^/]+)/bet/form/$',
        'bet_form', {
        }, 'bet_form'
    ),
)
