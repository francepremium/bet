from django.core import urlresolvers
from django.test import client

from yourlabs import smoke

from gsm.models import *

class Smoke(smoke.Smoke):
    def get_urls(self):
        for team in GsmEntity.objects.all():
            try:
                yield team.get_home_absolute_url()
            except urlresolvers.NoReverseMatch:
                pass
