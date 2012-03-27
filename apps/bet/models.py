import datetime
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

from bet import *
from gsm.models import session_played

logger = logging.getLogger('apps')

def bet_correct(sender, session, **kwargs):
    correct_for_session(session)
session_played.connect(bet_correct)

class BetProfile(models.Model):
    user = AutoOneToOneField(User, primary_key=True)
    offside_on = models.DateTimeField(null=True, blank=True)
    profitability = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    tickets = models.IntegerField()
    
    week_profitability = models.FloatField(default=0)
    week_profit = models.FloatField(default=0)
    week_tickets = models.IntegerField()
    
    month_profitability = models.FloatField(default=0)
    month_profit = models.FloatField(default=0)
    month_tickets = models.IntegerField()

    def calculate(self, tickets=None):
        context = {
            'total_odds': 0,
            'balance_history': [],
            'won_ticket_count': 0,
            'lost_ticket_count': 0,
            'won_ticket_percent': 0,
            'lost_ticket_percent': 0,
            'total_stake': 0,
            'total_odds': 0,
            'total_earnings': 0,
            'profit': 0,
            'profitability': 0,
            'average_odds': 0,
            'average_stake': 0,
        }
        context['total_odds'] = 0
        balance = 0

        if tickets is None:
            tickets = self.user.ticket_set.filter(status=TICKET_STATUS_DONE).exclude(
                bet__correction=BET_CORRECTION_NEW)

        if len(tickets) == 0:
            return context

        for ticket in tickets:
            balance += ticket.profit
            context['balance_history'].append({
                'ticket': ticket,
                'balance': int(balance),
            })

            context['total_odds'] += ticket.odds
            context['total_stake'] += ticket.stake
            
            if ticket.correction == BET_CORRECTION_WON:
                context['total_earnings'] += ticket.stake * ticket.odds
                context['won_ticket_count'] += 1
            elif ticket.correction == BET_CORRECTION_LOST:
                context['lost_ticket_count'] += 1


        context['average_odds'] = '%.2f' % (float(context['total_odds']) / len(tickets))
        context['won_ticket_percent'] = int(
            (float(context['won_ticket_count']) / len(tickets)) * 100)
        context['lost_ticket_percent'] = 100 - context['won_ticket_percent']
        context['average_stake'] = '%.2f' % (float(context['total_stake']) / len(tickets))
        context['profit'] = context['total_earnings'] - context['total_stake']
        if context['total_earnings'] > 0:
            context['profitability'] = '%.2f' % ((
                (context['total_earnings'] - context['total_stake']) / context['total_stake']
            ) * 100)
        else:
            context['profitability'] = 0

        context['total_earnings'] = float('%.2f' % context['total_earnings'])
        context['profit'] = float('%.2f' % context['profit'])

        self.profit = context['profit']
        self.profitability = context['profitability']
        self.save()

        return context

    def _calculate_for_tickets(self, tickets):
        if not len(tickets):
            return 0, 0

        profit = 0
        profitability = 0
        stake = 0

        for ticket in tickets:
            profit += ticket.profit
            stake += ticket.stake
        
        profitability = (profit / stake) * 100

        profitability = float('%.2f' % profitability)
        profit = float('%.2f' % profit)

        return profitability, profit

    def _refresh(self):
        today = datetime.date.today()

        tickets_base = self.user.ticket_set.filter(status=TICKET_STATUS_DONE).exclude(
            bet__correction=BET_CORRECTION_NEW)

        week_start_day = datetime.date.today() - datetime.timedelta(days=1)
        while week_start_day.weekday() != 3:
            week_start_day -= datetime.timedelta(days=1)
        week_tickets = tickets_base.filter(bet__session__start_datetime__gte=week_start_day)

        month_start_day = datetime.date.today() - datetime.timedelta(days=1)
        while month_start_day.day != 1:
            month_start_day -= datetime.timedelta(days=1)
        month_tickets = tickets_base.filter(bet__session__start_datetime__gte=month_start_day)


        self.profitability, self.profit = self._calculate_for_tickets(tickets_base)
        self.week_profitability, self.week_profit = self._calculate_for_tickets(week_tickets)
        self.month_profitability, self.month_profit = self._calculate_for_tickets(month_tickets)
        
        self.week_tickets = week_tickets.count()
        self.month_tickets = month_tickets.count()
        self.tickets = self.user.ticket_set.count()
        self.save()

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

    def copy(self):
        t = Ticket(
            bookmaker=self.bookmaker, 
            user=self.user, 
            stake=self.stake, 
            status=self.status
        )

        t.save()
        for b in self.bet_set.all():
            Bet(
                bettype=b.bettype,
                choice=b.choice,
                session=b.session,
                ticket=t,
                odds=b.odds,
                text=b.text,
                upload=b.upload,
                flagged=b.flagged,
                correction=b.correction,
                variable=b.variable,
                variable_hidden=b.variable_hidden,
            ).save()

    def is_won(self):
        return self.correction == BET_CORRECTION_WON
    def is_lost(self):
        return self.correction == BET_CORRECTION_LOST
    
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

def ticket_betprofile_refresh(sender, instance, **kwargs):
    if instance.correction != BET_CORRECTION_NEW:
        instance.user.betprofile.calculate()
signals.post_save.connect(ticket_betprofile_refresh, sender=Ticket)

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
    variable = models.CharField(max_length=200, null=True, blank=True)
    variable_hidden = models.CharField(max_length=200, null=True, blank=True)

    @property
    def get_variable(self):
        if self.variable_hidden:
            value = self.variable_hidden
        else:
            value = self.variable
        
        try:
            return float(value.replace(',', '.').strip())
        except ValueError, TypeError:
            self.flagged = True
            self.save()

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
        ordering = ('-session__start_datetime', '-id')

def bet_betprofile_refresh(sender, instance, **kwargs):
    if instance.correction != BET_CORRECTION_NEW:
        instance.ticket.user.betprofile.calculate()
signals.post_save.connect(bet_betprofile_refresh, sender=Bet)

def delete_empty_ticket(sender, **kwargs):
    try:
        if kwargs['instance'].ticket.bet_set.count() == 0:
            kwargs['instance'].ticket.delete()
    except Ticket.DoesNotExist:
        pass
signals.post_delete.connect(delete_empty_ticket, sender=Bet)

@spool
def refresh_betprofile_for_user(arguments):
    refresh_betprofile_for_user_nospool(arguments)

def refresh_betprofile_for_user_nospool(arguments):
    user = User.objects.get(pk=arguments['userpk'])
    logger.debug('triggered profile refresh %s' % user)
    print 'triggered profile refresh %s' % user
    if user.ticket_set.filter(status=TICKET_STATUS_DONE).count():
        logger.debug('starting user profile refresh %s' % user)
        data = user.betprofile._refresh()
        logger.debug('ending user profile refresh %s' % user)
    else:
        logger.debug('user %s has no ticket' % user)
    
    return uwsgi.SPOOL_OK
