from django.conf.urls.defaults import *

import views

urlpatterns = patterns('scoobet.views',
    url(
        r'leaderboard/$',
        views.homepage,
        name='scoobet_leaderboard',
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
