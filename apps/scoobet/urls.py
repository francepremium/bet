from django.conf.urls.defaults import *

import views

urlpatterns = patterns('scoobet.views',
    url(
        r'autocomplete/$',
        views.autocomplete,
        name='scoobet_autocomplete',
    ),
)
