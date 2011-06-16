from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('bookmaker.views',
    url(
        r'bet_type/choices/$',
        'choices_for_bettype', {
        }, 'bookmaker_choices_for_bettype',
    ),
    url(
        r'bet_type/for_bookmaker_and_sport/$',
        'bet_types_for_bookmaker_and_sport', {
        }, 'bookmaker_bet_types_for_bookmaker_and_sport',
    ),
    url(
        r'(?P<pk>[0-9]+)/bet_type/change/$',
        'change_bet_type', {
        }, 'bookmaker_change_bet_type',
    ),
    url(
        r'(?P<pk>[0-9]+)/bet_type/add/$',
        'add_bet_type', {
        }, 'bookmaker_add_bet_type',
    ),
    url(
        r'(?P<pk>[0-9]+)/bet_type/(?P<bettype_pk>[0-9]+)/edit/$',
        'edit_bet_type', {
        }, 'bookmaker_edit_bet_type',
    ),
    url(
        r'(?P<pk>[0-9]+)/bet_type/list/$',
        'list_bet_type', {
        }, 'bookmaker_list_bet_type',
    ),
    url(
        r'(?P<pk>[0-9]+)/edit/$',
        'edit', {
        }, 'bookmaker_edit',
    ),
    url(
        r'(?P<pk>[0-9]+)/file/$',
        'file', {
        }, 'bookmaker_file',
    ),
    url(
        r'(?P<pk>[0-9]+)/(?P<tab>[a-z]+)/$',
        'detail', {
        }, 'bookmaker_detail',
    ),
)
