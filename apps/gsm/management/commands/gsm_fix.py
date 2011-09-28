import logging
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import gsm
from gsm.models import *

logger = logging.getLogger('gsm_bugs')

class Command(BaseCommand):
    help = 'Delete all objects that raise HtmlInsteadOfXml'

    def handle(self, *args, **options):
        for e in GsmEntity.objects.all():
            self.test(e)
        
        for c in Championship.objects.all():
            self.test(c)

        for c in Competition.objects.all():
            self.test(c)

        for s in Season.objects.all():
            self.test(s)

        for r in Round.objects.all():
            self.test(r)

        for s in Session.objects.all():
            self.test(s)

    def test(self, e):
        try:
            gsm.get_tree('en', e.sport, 'get_%ss' % e.tag, 
                update=True, retry=True,
                type=e.tag, id=e.gsm_id)
        except gsm.HtmlInsteadOfXml:
            logger.error('%s %s %s' % (e.sport, e.tag, e.gsm_id))
