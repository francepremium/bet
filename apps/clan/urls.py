from django.conf.urls.defaults import *
from django.conf import settings
from django.views import generic

import views, models

urlpatterns = patterns('clan.views',
    url(
        r'fo/rm/$',
        'clan_form', {
        }, 'clan_form',
    ),
    url(
        r'(?P<slug>[^/]+)/join/$',
        'clan_join', {
        }, 'clan_join',
    ),
    url(
        r'(?P<slug>[^/]+)/quit/$',
        'clan_quit', {
        }, 'clan_quit',
    ),
    url(
        r'(?P<slug>[^/]+)/admin/$',
        'clan_admin', {
        }, 'clan_admin',
    ),
    url(
        r'(?P<slug>[^/]+)/$',
        generic.DetailView.as_view(
            model=models.Clan,
            context_object_name='clan'
        ),
        name='clan_detail',
    ),
    url(
        r'',
        generic.ListView.as_view(
            model=models.Clan, 
            queryset=models.Clan.objects.all(),
            context_object_name='clan_list'
        ),
        name='clan_list',
    ),
)

