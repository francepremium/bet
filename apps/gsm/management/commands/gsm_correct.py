import datetime, pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from gsm import *
from bet import *

class Command(BaseCommand):
    help = 'correct bets'

    def handle(self, *args, **options):
        sessions = Session.objects.exclude(status='Fixture')
        sessions = sessions.filter(bet__status=BET_STATUS_NEW)
