from django.core.management.base import BaseCommand, CommandError

import bet

class Command(BaseCommand):
    def handle(self, *args, **options):
        from bet.models import *
        from gsm.models import *

        sessions = Session.objects.filter(pk__in=Bet.objects.filter(
            correction=BET_CORRECTION_NEW).values_list('session_id'))
        for session in sessions:
            print 'session', session, session.pk, session.sport, session.gsm_id
            bet.correct_for_session(session)
