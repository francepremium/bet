from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('gsm.views',
    url(
        r'(?P<sport>[a-z]+)/team/(?P<gsm_id>[0-9]+)/$',
        'team_detail',
        name='gsm_team_detail'
    ),
    url(
        r'(?P<sport>[a-z]+)/team/(?P<gsm_id>[0-9]+)/(?P<tab>[a-z]+)/$',
        'team_detail_tab',
        name='gsm_team_detail_tab'
    ),
    url(
        r'(?P<sport>[a-z]+)/(?P<tag>[a-z_]+)/list/$',
        'entity_list',
        name='gsm_entity_list'
    ),
    url(
        r'(?P<sport>[a-z]+)/(?P<tag>[a-z_]+)/(?P<gsm_id>[0-9]+)/$',
        'entity_detail',
        name='gsm_entity_detail'
    ),
    url(
        r'(?P<sport>[a-z]+)/(?P<tab>[a-z]+)/$',
        'sport_detail_tab',
        name='gsm_sport_detail_tab'
    ),
    url(
        r'(?P<sport>[a-z]+)/$',
        'sport_detail',
        name='gsm_sport_detail'
    ),
)
