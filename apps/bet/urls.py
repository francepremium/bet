from django.conf.urls.defaults import *
from django.conf import settings

import views

urlpatterns = patterns('bet.views',
    url(
        r'list/flagged/$',
        views.BetListView.as_view(flagged=True), {
        }, 'bet_list_flagged'
    ),
    url(
        r'list/flagged/(?P<tab>[a-z]+)/$',
        views.BetListView.as_view(flagged=True), {
        }, 'bet_list_flagged_tab'
    ),
    url(
        r'list/to-correct/$',
        views.BetListView.as_view(to_correct=True), {
        }, 'bet_list_to_correct'
    ),
    url(
        r'list/to-correct/(?P<tab>[a-z]+)/$',
        views.BetListView.as_view(to_correct=True), {
        }, 'bet_list_to_correct_tab'
    ),
    url(
        r'list/$',
        views.BetListView.as_view(), {
        }, 'bet_list'
    ),
    url(
        r'list/(?P<tab>[a-z]+)/$',
        views.BetListView.as_view(), {
        }, 'bet_list_tab'
    ),
    url(
        r'ticket/(?P<ticket_pk>[^/]+)/delete/$',
        'ticket_delete', {
        }, 'bet_ticket_delete'
    ),
    url(
        r'ticket/(?P<pk>[0-9]+)/$',
        views.TicketDetailView.as_view(), {
        }, 'bet_ticket_detail',
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
    url(
        r'(?P<pk>[0-9]+)/$',
        views.BetDetailView.as_view(), {
        }, 'bet_detail',
    ),
    url(
        r'flag/$',
        views.bet_flag, {
        }, 'bet_flag'
    ),
)
