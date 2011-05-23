from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('bet.views',
    url(
        r'add/$',
        'add', {
        }, 'bet_add'
    )
)
