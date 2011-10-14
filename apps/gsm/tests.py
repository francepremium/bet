from django.utils import unittest
from django.test import TestCase

import gsm
from gsm.management.commands.gsm_sync_live import Command as GsmSyncLive
from bookmaker.models import *
from gsm.models import *
from bet.models import *

class LiveCorrectTestCase(TestCase):
    fixtures = [
        'users.json',
        'bookmaker.json',
        'match_959987.json',
    ]

    def setUp(self):
        self.session = Session.objects.get(gsm_id=959987, sport__slug='soccer')

    def test_correction(self):
        bettype = BetType.objects.get(name='1X2', sport__slug='soccer')
        bookmaker = Bookmaker.objects.get(name='Bwin.fr')
        ticket = Ticket(user=User.objects.get(username='test'), stake=4)
        ticket.bookmaker = bookmaker
        ticket.save()

        b1 = Bet(session=self.session, bettype=bettype, ticket=ticket, odds=5)
        b1.choice = bettype.betchoice_set.get(name='1')
        b1.save()
        bx = Bet(session=self.session, bettype=bettype, ticket=ticket, odds=5)
        bx.choice = bettype.betchoice_set.get(name='X')
        bx.save()
        b2 = Bet(session=self.session, bettype=bettype, ticket=ticket, odds=5)
        b2.choice = bettype.betchoice_set.get(name='2')
        b2.save()

        root = gsm.get_tree('en', 'soccer', 'get_matches', 
            id=self.session.gsm_id, type='match')

        for element in gsm.parse_element_for(root.getroot(), 'match'):
            GsmSyncLive().correct(element, self.session)
         
        b1 = Bet.objects.get(pk=b1.pk)
        self.assertEqual(b1.status, BET_STATUS_CORRECTED)
        self.assertEqual(b1.correction, BET_CORRECTION_LOST)        
        bx = Bet.objects.get(pk=bx.pk)
        self.assertEqual(bx.status, BET_STATUS_CORRECTED)
        self.assertEqual(bx.correction, BET_CORRECTION_LOST)       
        b2 = Bet.objects.get(pk=b2.pk)
        self.assertEqual(b2.status, BET_STATUS_CORRECTED)
        self.assertEqual(b2.correction, BET_CORRECTION_WON)
