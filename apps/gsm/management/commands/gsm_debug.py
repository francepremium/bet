import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import gsm
from gsm.models import *

class Command(BaseCommand):
    args = '<sport/tag/gsm_id>'
    help = 'get debug info for a GSM'

    def handle(self, *args, **options):
        e = gsm.get_object_from_url(args[0])
        
        if tag == 'team':
            if not e.get_sessions().count():
                print "Team has no sessions"
