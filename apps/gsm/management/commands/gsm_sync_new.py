import datetime
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import gsm
from gsm.sync import *
from gsm.models import *

logger = logging.getLogger('gsm')

class Command(BaseCommand):
    def handle(self, *args, **options):
        sport = Sport.objects.get(slug='soccer')
        last_updated = datetime.datetime.now() - datetime.timedelta(days=1)
        minimal_date = datetime.datetime.now() - datetime.timedelta(years=2)

        sync = Sync(sport, last_updated, minimal_date, logger)
        sync.sync_by_get_seasons()
