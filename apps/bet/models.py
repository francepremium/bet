from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

class Bet(models.Model):
    bookmaker = models.ForeignKey('bookmaker.Bookmaker')
    bettype = models.ForeignKey('bookmaker.BetType')
    choice = models.ForeignKey('bookmaker.BetChoice', null=True)
    session = models.ForeignKey('gsm.Session')
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return '%s: %s' % (self.type, self.choice)
