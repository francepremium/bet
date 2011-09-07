from django.core import urlresolvers
from django.test import client

from yourlabs import smoke

from gsm.models import *

class Smoke(smoke.Smoke):
    def get_urls(self):
        methods = {
            'team': (
                'get_home_absolute_url',
                'get_squad_absolute_url',
                'get_statistics_absolute_url',
                'get_calendar_absolute_url',
                'get_picks_absolute_url',
            ),
            'person': [],
            'double': [],
        }
        for entity in GsmEntity.objects.all():
            for method in methods[entity.tag]:
                yield smoke.SmokeUrl(
                    getattr(entity, method)(),
                    '%s, %s, %s' % (
                        method,
                        entity.tag,
                        entity.sport.slug
                    )
                )
