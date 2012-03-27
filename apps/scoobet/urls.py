from django.conf.urls.defaults import *
from django.views.generic import simple

import views

urlpatterns = patterns('scoobet.views',
    url(
        r'leaderboard/$',
        simple.redirect_to, {
            'url': 'leaderboard/week/',
        }, 'scoobet_leaderboard',
    ),
    url(
        r'leaderboard/all/$',
        views.leaderboard,
        name='scoobet_leaderboard_all',
    ),
    url(
        r'leaderboard/week/$',
        views.leaderboard, {
            'tab': 'week',
        }, 'scoobet_leaderboard_week',
    ),
    url(
        r'leaderboard/month/$',
        views.leaderboard, {
            'tab': 'month',
        }, name='scoobet_leaderboard_month',
    ),
    url(
        r'status/add/$',
        views.status_add,
        name='scoobet_status_add',
    ),
    url(
        r'autocomplete/$',
        views.autocomplete,
        name='scoobet_autocomplete',
    ),
    url(
        r'autocomplete/friends/$',
        views.following_autocomplete,
        name='scoobet_following_autocomplete',
    ),
    url(
        r'feed/friends/$',
        views.feed_friends,
        name='scoobet_feed_friends',
    ),
    url(
        r'avatar/upload/$',
        views.avatar_upload,
        name='scoobet_upload_avatar',
    ),
)
