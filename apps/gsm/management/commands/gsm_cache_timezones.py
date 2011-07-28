import datetime, pytz

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    args = 'n/a'
    help = 'generate timezones cache'

    def handle(self, *args, **options):
