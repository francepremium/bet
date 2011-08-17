import logging

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

try:
    import uwsgi
    from uwsgidecorators import spool
except ImportError:
    print "MOCKING what we need of uwsgi"
    class uwsgi(object):
        SPOOL_RETRY = False
    def spool(func):
        return func

from annoying.fields import AutoOneToOneField

logger = logging.getLogger('apps')

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
    offside_on = models.DateTimeField(null=True, blank=True)
    profitability = models.FloatField(default=0)
    profit = models.FloatField(default=0)

    def is_offside(self):
        if not hasattr(self, '_is_offside'):
            if not self.offside_on:
                self._is_offside = False
            else:
                delta = datetime.datetime.now() - self.offside_on
                if delta.days <= 2:
                    self._is_offside = True
                else:
                    self._is_offside = False

                errors = self.event_set.filter(datetime__gte=datetime.timedelta(2))
                errors = errors.filter(valid=False)
                if errors.count():
                    self.offside_on = datetime.datetime.now()
                    self._is_offside = True
                    self.save()
        return self._is_offside

    def is_referee(self):
        if not hasattr(self, '_is_referee'):
            if self.user.is_staff:
                self._is_referee = True
            elif self.is_offside():
                self._is_referee = False
            elif self.get_event_set_percent(self.user.event_set.filter(valid=False)) > 5:
                self._is_referee = False
            elif self.user.event_set.filter(valid=True).count() < 50:
                self._is_referee = False
            else:
                self._is_referee = True
        return self._is_referee
   
    def get_event_set_percent(self, event_set):
        total_events = self.user.event_set.all().count()
        if total_events == 0:
            return 0
        percent = ( event_set.count() / total_events ) * 100
        return percent

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

        return True

    def refresh(self):
        logger.debug('spooling user profile refresh %s' % self.user)
        refresh_betprofile_for_user.spool(userpk=str(self.user.pk))

class Ticket(models.Model):
    TICKET_STAKE_CHOICES = [(x,x) for x in range(1,11)]
    TICKET_STATUS_CHOICES = (
        (TICKET_STATUS_INCOMPLETE, _('incomplete')),
        (TICKET_STATUS_DONE, _('done')),
    )

    bookmaker = models.ForeignKey('bookmaker.Bookmaker')
    user = models.ForeignKey('auth.User')
    stake = models.IntegerField(choices=TICKET_STAKE_CHOICES)
    status = models.IntegerField(choices=TICKET_STATUS_CHOICES, default=TICKET_STATUS_INCOMPLETE)
    creation_datetime = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return urlresolvers.reverse('bet_ticket_detail', args=(self.pk,))

    def __unicode__(self):
        return '#%s' % self.pk

    @property
    def correction(self):
        if not hasattr(self, '_correction'):
            # if any bet is "new"
            if self.bet_set.filter(correction=BET_CORRECTION_NEW).count():
                self._correction = BET_CORRECTION_NEW
            elif self.bet_set.filter(correction=BET_CORRECTION_LOST).count():
                self._correction = BET_CORRECTION_LOST
            else:
                self._correction = BET_CORRECTION_WON
        return self._correction

    def get_correction_display(self):
        if not hasattr(self, '_correction_display'):
            for value, display in Bet.BET_CORRECTION_CHOICES:
                if value == self.correction:
                    self._correction_display = display
                    break
        return self._correction_display

    @property
    def get_odds_display(self):
        return "%.2f" % self.odds

    @property
    def odds(self):
        if not hasattr(self, '_odds'):
            i = 1
            for bet in self.bet_set.all():
                if bet.correction != BET_CORRECTION_CANCELED:
                    i = i * bet.odds
            self._odds = i
        return self._odds

    @property
    def profit(self):
        if not hasattr(self, '_profit'):
            if self.correction == BET_CORRECTION_WON:
                self._profit = ( self.odds * self.stake ) - self.stake
            elif self.correction == BET_CORRECTION_LOST:
                self._profit = self.stake * -1
            else:
                self._profit = 0
        return self._profit

    @property
    def ticket_bet_count(self):
        if not hasattr(self, '_ticket_bet_count'):
            if hasattr(self, 'ticket__bet__count'):
                self._ticket_bet_count = self.ticket__bet__count
            else:
                self._ticket_bet_count = self.ticket.bet_set.count()
        return self._ticket_bet_count

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
        (BET_CORRECTION_NEW, _('waiting')),
        (BET_CORRECTION_WON, _('won')),
        (BET_CORRECTION_LOST, _('lost')),
        (BET_CORRECTION_CANCELED, _('canceled')),
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
    
    def get_absolute_url(self):
        return urlresolvers.reverse('bet_detail', args=(self.pk,))

def delete_empty_ticket(sender, **kwargs):
    try:
        if kwargs['instance'].ticket.bet_set.count() == 0:
            kwargs['instance'].ticket.delete()
    except Ticket.DoesNotExist:
        pass
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

@spool
def refresh_betprofile_for_user(arguments):
    user = User.objects.get(pk=arguments['userpk'])
    logger.debug('triggered profile refresh %s' % user)
    print 'triggered profile refresh %s' % user
    if user.ticket_set.filter(status=TICKET_STATUS_DONE).count():
        logger.debug('starting user profile refresh %s' % user)
        tickets = user.ticket_set.filter(status=TICKET_STATUS_DONE)

        total_odds = 0
        balance = 0
        won_ticket_count = 0
        lost_ticket_count = 0
        total_stake = 0
        total_earnings = 0

        for ticket in tickets:
            balance += ticket.profit

            total_odds += ticket.odds
            total_stake += ticket.stake
            
            if ticket.correction == BET_CORRECTION_WON:
                total_earnings += ticket.stake * ticket.odds
                won_ticket_count += 1
            elif ticket.correction == BET_CORRECTION_LOST:
                lost_ticket_count += 1

        average_odds = '%.2f' % (float(total_odds) / len(tickets))
        won_ticket_percent = int(
            (float(won_ticket_count) / len(tickets)) * 100)
        lost_ticket_percent = 100 - won_ticket_percent
        average_stake = '%.2f' % (float(total_stake) / len(tickets))
        profit = total_earnings - total_stake
        if total_earnings > 0:
            profitability = '%.2f' % ((
                (total_earnings - total_stake) / total_stake
            ) * 100)
            int((total_stake / total_earnings)*100)
        else:
            profitability = 0

        user.betprofile.profit = profit
        user.betprofile.profitability = profitability
        user.betprofile.save()
        logger.debug('ending user profile refresh %s' % user)
    else:
        logger.debug('user %s has no ticket' % user)
