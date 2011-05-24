from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

class Bet(models.Model):
    STAKES = (
        (0, 0),
    )

    bookmaker = models.ForeignKey('bookmaker.Bookmaker')
    user = models.ForeignKey('auth.User')
    stake = models.IntegerField(choices=STAKE_CHOICES)

    def __unicode__(self):
        return '#%s' % self.pk

class Pronostic(models.Model):
    bettype = models.ForeignKey('bookmaker.BetType')
    choice = models.ForeignKey('bookmaker.BetChoice', null=True)
    session = models.ForeignKey('gsm.Session')
    bet = models.ForeignKey('Bet')

    def __unicode__(self):
        return '%s: %s' % (self.bettype, self.choice)
