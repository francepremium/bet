import re
import htmlentitydefs
import urllib
import datetime

from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

def logo_upload_to(instance, filename):
    return 'bookmaker/%s/%s' % (instance.pk, filename)

class Bookmaker(models.Model):
    user = models.OneToOneField('auth.User')
    name = models.CharField(max_length=100, unique=True)
    creation_date = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    url = models.URLField()
    email = models.EmailField()
    live_bets = models.BooleanField()
    logo = models.ImageField(upload_to=logo_upload_to, null=True, blank=True)
    bettype = models.ManyToManyField('BetType', null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
    
    def sports(self):
        return BetType.sport.field.rel.to.objects.filter(
            bettype__bookmaker=self).distinct()

class BetType(models.Model):
    name = models.CharField(max_length=100)
    sport = models.ForeignKey('gsm.Sport')
    creation_bookmaker = models.ForeignKey('Bookmaker', related_name='created_bettype', null=True)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.sport)
    
    class Meta:
        ordering = ['sport', 'name']
        unique_together = (('name_fr', 'sport'),('name_en', 'sport'))

class BetChoice(models.Model):
    bettype = models.ForeignKey('BetType')
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
