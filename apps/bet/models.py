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
        SPOOL_OK = True
    def spool(func):
        return func

from annoying.fields import AutoOneToOneField

logger = logging.getLogger('apps')

TICKET_STATUS_INCOMPLETE = 0
TICKET_STATUS_DONE = 1

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
        # if any bet is "new"
        if self.bet_set.filter(correction=BET_CORRECTION_NEW).count():
            return BET_CORRECTION_NEW
        elif self.bet_set.filter(correction=BET_CORRECTION_LOST).count():
            return BET_CORRECTION_LOST
        else:
            return BET_CORRECTION_WON

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
            self._odds = float('%.2f' % i)
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
            
            self._profit = float('%.2f' % self._profit)
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
    flagged = models.BooleanField()
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

    class Meta:
        ordering = ('-id',)

def delete_empty_ticket(sender, **kwargs):
    try:
        if kwargs['instance'].ticket.bet_set.count() == 0:
            kwargs['instance'].ticket.delete()
    except Ticket.DoesNotExist:
        pass
signals.post_delete.connect(delete_empty_ticket, sender=Bet)

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
    
    return uwsgi.SPOOL_OK
