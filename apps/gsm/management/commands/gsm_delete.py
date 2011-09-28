import logging
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import gsm
from gsm.models import *

logger = logging.getLogger('gsm_delete')

class Command(BaseCommand):
    help = 'get debug info for a GSM'

    def handle(self, *args, **options):
        for sport in Sport.objects.all():
            t = gsm.get_tree('en', sport, 'get_deleted', 
                update=True, retry=True)

            for c in t.getroot().getchildren():
                try:
                    gsm_ids = [x.attrib['source_id'] for x in c.getchildren()]
                except KeyError:
                    continue
                
                if c.tag == 'match':
                    cls = Session
                elif c.tag == 'round':
                    cls = Round
                elif c.tag == 'season':
                    cls = Season
                elif c.tag == 'competition':
                    cls = Competition
                elif c.tag == 'person':
                    cls = GsmEntity
                elif c.tag == 'team':
                    cls = GsmEntity
                elif c.tag == 'double':
                    cls = GsmEntity
                else:
                    continue

                for i in gsm_ids:
                    logger.info('Deleting %s with id %s from sport %s' % (
                        cls.__name__, i, sport))

                cls.objects.filter(gsm_id__in=gsm_ids, sport=sport
                    ).delete()
