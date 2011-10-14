from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import gsm
from gsm.models import *
from bet.models import *
from bookmaker.models import *

copy_map = {
    'fs_%s': '%s_score',
    'eps_%s': '%s_ets',
    'eps_%s': '%s_eps',
    'status': 'status',
    'p1s_%s': '%s1_score',
    'p2s_%s': '%s2_score',
    'p3s_%s': '%s3_score',
    'p4s_%s': '%s4_score',
    'eps_%s': '%s5_score',
}

logger = logging.getLogger('gsm')

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--nowplaying',
            dest='nowplaying',
            default=False,
            action="store_true",
            help='set to call get_matches_live with nowplaying=yes'
        ),
        make_option('--cooldown',
            dest='cooldown',
            default=False,
            help='cooldown time between requests'
        ),
    )

    def handle(self, *args, **options):
        self.cooldown = int(options.get('cooldown', 1))

        now_playing = options.get('nowplaying', False)
        now = datetime.datetime.now()
        delta = datetime.timedelta(hours=4)
        sport = Sport.objects.get(slug='soccer')
        for sport in Sport.objects.all():
            if sport.slug == 'soccer':
                tree = gsm.get_tree('en', sport, 'get_matches_live', update=True, now_playing=now_playing)
                self.update(tree, sport)
                time.sleep(self.cooldown)
            else:
                sessions = Session.objects.filter(
                    datetime_utc__gte=now - delta,
                    datetime_utc__lte=now + delta,
                    sport=sport
                )
                for session in sessions:
                    tree = gsm.get_tree('en', sport, 'get_matches', update=True, type=session.tag, id=session.gsm_id)
                    self.update(tree, sport)
                    time.sleep(self.cooldown)

    def update(self, tree, sport):
        root = tree.getroot()
        for element in gsm.parse_element_for(root, 'match'):
            try:
                session = Session.objects.get(gsm_id=element.attrib['match_id'], sport=sport)
                session.resync(element)
                self.correct(element, session)
            except Session.DoesNotExist:
                logger.error('Could not sync session that does not exist: %s' % element.attrib['match_id'])
    
    def correct(self, element, session):
        if element.attrib['status'] in ('Fixture', 'Playing'):
            return
        
        if element.attrib['status'] == 'Cancelled':
            Bet.objects.filter(session=session).update(correction=BET_CORRECTION_CANCELED, status=BET_STATUS_CORRECTED)
            return

        rewrite = (
            'fs_A',
            'fs_B',
            'ets_A',
            'ets_B',
        )

        to_correct = BetType.objects.filter(bet__session=session).distinct()
        for t in to_correct:
            for c in t.betchoice_set.all():
                try:
                    condition = c.condition
                    for var in rewrite:
                        condition = condition.rewrite(var, 'element.attrib["%s"]' % var)
                    result = eval(condition)
                    if result:
                        correction = BET_CORRECTION_WON
                    else:
                        correction = BET_CORRECTION_LOST

                    Bet.objects.filter(session=session, bettype=t, choice=c).update(correction=correction)
                except:
                    Bet.objects.filter(session=session, bettype=t, choice=c).update(flagged=True)
