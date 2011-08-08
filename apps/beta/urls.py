from django.conf.urls.defaults import *

urlpatterns = patterns('beta.views',
    url(r'', 'homepage', name='beta_homepage'),
)
