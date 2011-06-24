from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

import views

handler500 = "pinax.views.server_error"

urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),
    url(r"^gsm/", include('gsm.urls')),
    url(r"^clan/", include('clan.urls')),
    url(r'^avatar/', include('avatar.urls')),
    url(r"^bet/", include('bet.urls')),
    # url(r"^postman/", include('postman.urls')),
    url(r"^article/", include('article.urls')),
    url(r"^actstream/", include('actstream.urls')),
    url(r"^bookmaker/", include('bookmaker.urls')),
    url(r"^account/", include('pinax.apps.account.urls')),
    url(r"^localeurl/", include('localeurl.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r"^admin/", include(admin.site.urls)),
    url(r'^ajax_select/', include('ajax_select.urls')),
    url(r'^me/$', 'scoobet.views.me', name='me'),
    url(
        r'^(?P<session_pk>[0-9]+)/(?P<bettype_pk>[0-9]+)/$',
        views.session_bettype_detail, {
        }, 'session_bettype_detail',
    ),
    url(r"^users/(?P<username>[^/]+)/$", 'scoobet.views.user_detail', name='user_detail'),
    url(r"^users/(?P<username>[^/]+)/(?P<tab>[^/]+)/$", 'scoobet.views.user_detail', name='user_detail_tab'),
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
