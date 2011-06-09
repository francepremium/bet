from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from annoying.fields import AutoOneToOneField

TICKET_STATUS_INCOMPLETE = 0
TICKET_STATUS_DONE = 1

BET_STATUS_NEW = 0
BET_STATUS_CORRECTED = 1
BET_STATUS_FLAG = 2

BET_CORRECTION_NEW = 0
BET_CORRECTION_WON = 1
BET_CORRECTION_CANCELED = 2
BET_CORRECTION_LOST = 3

EVENT_KIND_CORRECTION = 1
EVENT_KIND_FLAG = 2

class BetProfile(models.Model):
    user = AutoOneToOneField(User, primary_key=True)

    def is_offside(self):
        return False

    def is_referee(self):
        return False

    def can_correct(self, bet):
        if self.is_offside():
            return False

        if bet.is_new():
            # anyone can correct any new bet
            return True

        if bet.is_flag() and self.is_referee():
            # referees can correct flagged bets
            return True

        return False

    def can_flag(self, bet):
        if self.is_offside():
            return False
        
        if bet.is_flag():
            # cannot flag an already flagged bet
            return False

        if bet.is_won() or bet.is_lost():
            # anyone can flag corrected bet
            return True

        return False

class Ticket(models.Model):
    TICKET_STAKE_CHOICES = [(x,x) for x in range(1,10)]
    TICKET_STATUS_CHOICES = (
        (TICKET_STATUS_INCOMPLETE, _('incomplete')),
        (TICKET_STATUS_DONE, _('done')),
    )

    bookmaker = models.ForeignKey('bookmaker.Bookmaker')
    user = models.ForeignKey('auth.User')
    stake = models.IntegerField(choices=TICKET_STAKE_CHOICES)
    status = models.IntegerField(choices=TICKET_STATUS_CHOICES, default=TICKET_STATUS_INCOMPLETE)

    def __unicode__(self):
        return '#%s' % self.pk

    @property
    def odds(self):
        odds = self.pronostic_set.all().values_list('odds', flat=True)
        i = 1
        for odd in odds:
            i = i * odd
        return i

def media_upload_to(instance, filename):
    return 'ticket/%s/%s' % (instance.ticket.pk, filename)

class Bet(models.Model):
    BET_STATUS_CHOICES = (
        (None, '---------'),
        (BET_STATUS_NEW, _('new')),
        (BET_STATUS_CORRECTED, _('corrected')),
        (BET_STATUS_FLAG, _('flagged for moderation')),
    )

    BET_CORRECTION_CHOICES = (
        (BET_CORRECTION_NEW, _('new')),
        (BET_CORRECTION_WON, _('won')),
        (BET_CORRECTION_LOST, _('lost')),
    )

    bettype = models.ForeignKey('bookmaker.BetType')
    choice = models.ForeignKey('bookmaker.BetChoice', null=True)
    session = models.ForeignKey('gsm.Session')
    ticket = models.ForeignKey('Ticket')
    odds = models.DecimalField(max_digits=4, decimal_places=2)
    text = models.TextField(blank=True, null=True)
    upload = models.FileField(upload_to=media_upload_to, null=True, blank=True)
    status = models.IntegerField(choices=BET_STATUS_CHOICES, default=BET_STATUS_NEW)
    correction = models.IntegerField(choices=BET_CORRECTION_CHOICES, default=BET_CORRECTION_NEW)

    def __unicode__(self):
        return u'%s: %s' % (self.bettype, self.choice)

    def is_new(self):
        return self.status == BET_STATUS_NEW
    def is_corrected(self):
        return self.status >= BET_STATUS_CORRECTED
    def is_flag(self):
        return self.status == BET_STATUS_FLAG
    def is_won(self):
        return self.correction == BET_CORRECTION_WON
    def is_lost(self):
        return self.correction == BET_CORRECTION_LOST
    def is_canceled(self):
        return self.correction == BET_CORRECTION_CANCELED

def delete_empty_ticket(sender, **kwargs):
    if kwargs['instance'].ticket.bet_set.count() == 0:
        kwargs['instance'].ticket.delete()
signals.post_delete.connect(delete_empty_ticket, sender=Bet)

class Event(models.Model):
    EVENT_KIND_CHOICES = (
        (EVENT_KIND_CORRECTION, _('correction')),
        (EVENT_KIND_FLAG, _('flag')),
    )

    bet = models.ForeignKey('Bet')
    user = models.ForeignKey('auth.User')
    correction = models.IntegerField(choices=Bet.BET_CORRECTION_CHOICES, default=BET_CORRECTION_NEW)
    datetime = models.DateTimeField(auto_now_add=True)
    kind = models.IntegerField(choices=EVENT_KIND_CHOICES)
    valid = models.BooleanField(default=True)

    def __unicode__(self):
        if self.kind == EVENT_KIND_CORRECTION:
            verb = _(u'corrected')
        elif self.kind == EVENT_KIND_FLAG:
            verb = _(u'flagged')

        return _(u'%(user)s %(verb)s %(bettype)s on match %(session)s, result: %(correction)s') % {
            'user': self.user,
            'verb': verb,
            'bettype': self.bet.bettype,
            'session': self.bet.session,
            'correction': self.correction,
        }
