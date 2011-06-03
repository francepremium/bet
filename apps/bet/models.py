from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType

TICKET_STATUS_INCOMPLETE = 0
TICKET_STATUS_DONE = 1

BET_STATUS_NEW = 0
BET_STATUS_CHECKED = 1
BET_STATUS_FLAGGED = 2

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
        (BET_STATUS_NEW, _('new')),
        (BET_STATUS_CHECKED, _('verified')),
        (BET_STATUS_FLAGGED, _('flagged for moderation')),
    )

    bettype = models.ForeignKey('bookmaker.BetType')
    choice = models.ForeignKey('bookmaker.BetChoice', null=True)
    session = models.ForeignKey('gsm.Session')
    ticket = models.ForeignKey('Ticket')
    odds = models.DecimalField(max_digits=4, decimal_places=2)
    text = models.TextField(blank=True, null=True)
    upload = models.FileField(upload_to=media_upload_to, null=True, blank=True)
    status = models.IntegerField(choices=BET_STATUS_CHOICES, default=BET_STATUS_NEW)

    def __unicode__(self):
        return '%s: %s' % (self.bettype, self.choice)

def delete_empty_ticket(sender, **kwargs):
    if kwargs['instance'].ticket.bet_set.count() == 0:
        kwargs['instance'].ticket.delete()
signals.post_delete.connect(delete_empty_ticket, sender=Bet)
