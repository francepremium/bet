import re
import htmlentitydefs
import urllib
import datetime
from lxml import etree

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

class Sport(models.Model):
    name = models.CharField(max_length=30, editable=False)

    def __unicode__(self):
        return _(self.name)
    
    class Meta:
        ordering = ('-name',)

class Tour(models.Model):
    gsm_id = models.IntegerField(editable=False)
    sport = models.ForeignKey('Sport')

    name = models.CharField(max_length=30, editable=False)
    last_updated = models.DateTimeField(editable=False, null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)

class Season(models.Model):
    gsm_id = models.IntegerField(editable=False)

    competition = models.ForeignKey('Competition')
    name = models.CharField(max_length=30, editable=False)

    # tennis specific
    gender = models.CharField(max_length=12, null=True, blank=True, editable=False)
    prize_money = models.IntegerField(null=True, blank=True)
    prize_currency = models.CharField(max_length=3, null=True, blank=True)
    type = models.CharField(max_length=12, null=True, blank=True, editable=False)
    
    # soccer specific
    service_level = models.IntegerField(null=True, blank=True, editable=False)

    start_date = models.DateTimeField(editable=False)
    end_date = models.DateTimeField(editable=False)
    last_updated = models.DateTimeField(editable=False, null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)

class Competition(models.Model):
    gsm_id = models.IntegerField(editable=False)
    display_order = models.IntegerField(editable=False)

    sport = models.ForeignKey('Sport')
    area = models.ForeignKey('Area')
    tour = models.ForeignKey('Tour', null=True, blank=True)

    name = models.CharField(max_length=100, editable=False)
    type = models.CharField(max_length=12, null=True, blank=True, editable=False)
    format = models.CharField(max_length=12, null=True, blank=True, editable=False)
    soccer_type = models.CharField(max_length=12, null=True, blank=True, editable=False)
    court_type = models.CharField(max_length=12, null=True, blank=True, editable=False)
    team_type = models.CharField(max_length=12, null=True, blank=True, editable=False)
    display_order = models.IntegerField(editable=False, null=True, blank=True)
    last_updated = models.DateTimeField(editable=False, null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)

class Area(models.Model):
    parent = models.ForeignKey('Area', null=True, blank=True, editable=False)
    gsm_id = models.IntegerField(editable=False)
    country_code = models.CharField(max_length=3, editable=False)
    name = models.CharField(max_length=100, editable=False)

    def __unicode__(self):
        return self.name
    
    class Meta:
        order_with_respect_to = 'parent'
        ordering = ('-name',)
