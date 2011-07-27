from django.conf.urls.defaults import *

import views

urlpatterns = patterns('scoobet.views',
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
        views.friends_autocomplete,
        name='scoobet_friends_autocomplete',
    ),
    url(
        r'feed/friends/$',
        views.feed_friends,
        name='scoobet_feed_friends',
    ),
)
