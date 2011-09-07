import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from gsm.models import *

class Command(BaseCommand):
    args = '<sport/tag/gsm_id>'
    help = 'get debug info for a GSM'

    def handle(self, *args, **options):
        args = args[0].split('/')
        sport = args[0]
        tag = args[1]
        gsm_id = args[2]

        e = GsmEntity.objects.get(sport__slug=sport, tag=tag, gsm_id=gsm_id)
        
        if tag == 'team':
            if not e.get_sessions().count():
                print "Team has no sessions"
