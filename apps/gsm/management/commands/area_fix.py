import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from gsm.models import *

class Command(BaseCommand):
    args = 'n/a'
    help = 'fix gsm areas'

    def handle(self, *args, **options):
        for a in Area.objects.filter(country_code_2=""):
            print "Enter 2 letters code for", a
            value = raw_input()
            print ""
            if value:
                a.country_code_2 = value.strip().lower()
                a.save()
                print "Saved %s for %s" % (value, a)
