from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('gsm.views',
    url(
        r'(?P<sport>[a-z]+)/(?P<tab>[a-z]+)/$',
        'sport_detail',
        name='gsm_sport_detail_tab'
    ),
    url(
        r'(?P<sport>[a-z]+)/(?P<tag>[a-z_]+)/$',
        'entity_list',
        name='gsm_entity_list'
    ),
    url(
        r'(?P<sport>[a-z]+)/(?P<tag>[a-z_]+)/(?P<gsm_id>[0-9]+)/$',
        'entity_detail',
        name='gsm_entity_detail'
    )
)
