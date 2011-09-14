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
        for entity in GsmEntity.objects.all().select_related('sport'):
            for method in methods[entity.tag]:
                if entity.sport.slug != 'soccer' and method == 'get_statistics_absolute_url':
                    continue
                if method == 'get_squad_absolute_url' and not entity.has_squad():
                    continue
                    
                yield smoke.SmokeUrl(
                    getattr(entity, method)(),
                    (
                        method,
                        entity.tag,
                        entity.sport.slug
                    )
                )
