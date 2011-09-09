from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import gsm
from gsm.models import *

def parse_element_for(parent, tag):
    for element in parent.getchildren():
        if element.tag == tag:
            yield element
        else:
            for subelement in parse_element_for(element, tag):
                yield subelement

copy_map = {
    'soccer': (
        'fs_A',
        'fs_B',
        'hts_A',
        'hts_B',
        'ets_A',
        'ets_B',
        'ps_A',
        'ps_B',
    )
}

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--nowplaying',
            dest='nowplaying',
            default=False,
            action="store_true",
            help='set to call get_matches_live with nowplaying=yes'
        ),
    )

    def handle(self, *args, **options):
        now_playing = options.get('nowplaying', False)
        sport = Sport.objects.get(slug='soccer')
        tree = gsm.get_tree('en', sport, 'get_matches_live', now_playing=now_playing)
        root = tree.getroot()
        for element in parse_element_for(root, 'match'):
            session = Session.objects.get(gsm_id=element.attrib['match_id'])
            for src in copy_map[sport.slug]:
                if src == 'status':
                    dst = 'session_status'
                else:
                    dst = src
                session.src = element.attrib[dst]

            session.save()
