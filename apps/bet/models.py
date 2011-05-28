from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

class Bet(models.Model):
    STAKE_CHOICES = [(x,x) for x in range(1,10)]

    bookmaker = models.ForeignKey('bookmaker.Bookmaker')
    user = models.ForeignKey('auth.User')
    stake = models.IntegerField(choices=STAKE_CHOICES)

    def __unicode__(self):
        return '#%s' % self.pk

    @property
    def odds(self):
        odds = self.pronostic_set.all().values_list('odds', flat=True)
        i = 1
        for odd in odds:
            i = i * odd
        return i

class Pronostic(models.Model):
    bettype = models.ForeignKey('bookmaker.BetType')
    choice = models.ForeignKey('bookmaker.BetChoice', null=True)
    session = models.ForeignKey('gsm.Session')
    bet = models.ForeignKey('Bet')
    odds = models.DecimalField(max_digits=4, decimal_places=2)

    def __unicode__(self):
        return '%s: %s' % (self.bettype, self.choice)
