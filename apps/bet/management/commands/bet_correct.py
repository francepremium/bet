from django.core.management.base import BaseCommand, CommandError

import bet

class Command(BaseCommand):
    def handle(self, *args, **options):
        from bet.models import *
        from gsm.models import *

        sessions = Session.objects.filter(pk__in=Bet.objects.values_list('session_id'))
        for session in sessions:
            bet.correct_for_session(session)
