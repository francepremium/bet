from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('gsm.views')

for tag in ('team', 'competition', 'session', 'person'):
    urlpatterns += patterns('gsm.views',
        url(
            r'(?P<sport>[a-z]+)/%s/(?P<gsm_id>[0-9]+)/$' % tag,
            '%s_detail_tab' % tag, {
                'tab': 'home',
            }, 'gsm_%s_detail' % tag
        ),
        url(
            r'(?P<sport>[a-z]+)/%s/(?P<gsm_id>[0-9]+)/(?P<tab>[a-z]+)/$' % tag,
            '%s_detail_tab' % tag, {
            }, 'gsm_%s_detail_tab' % tag
        ),
    )

urlpatterns += patterns('gsm.views',
    url(
        r'(?P<sport>[a-z]+)/(?P<tag>[a-z_]+)/list/$',
        'entity_list', {
        }, 'gsm_entity_list'
    ),
    url(
        r'(?P<sport>[a-z]+)/(?P<tag>[a-z_]+)/(?P<gsm_id>[0-9]+)/$',
        'entity_detail', {
        }, 'gsm_entity_detail'
    ),
    url(
        r'json/sessions/$',
        'sport_json_sessions', {
        }, 'gsm_sport_json_sessions'
    ),
    url(
        r'json/competitions/$',
        'sport_json_competitions', {
        }, 'gsm_sport_json_competitions'
    ),
    url(
        r'(?P<sport>[a-z]+)/(?P<tab>[a-z]+)/$',
        'sport_detail_tab', {
        }, 'gsm_sport_detail_tab'
    ),
    url(
        r'(?P<sport>[a-z]+)/$',
        'sport_detail', {
        }, 'gsm_sport_detail'
    ),
)
