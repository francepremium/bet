import re
import htmlentitydefs
import urllib
import datetime

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache

from autoslug import AutoSlugField

class Sport(models.Model):
    name = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from='name')

    def __unicode__(self):
        return _(self.name)
    
    class Meta:
        ordering = ('-name',)

class Championship(models.Model):
    gsm_id = models.IntegerField()
    sport = models.ForeignKey('Sport')

    name = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from='name_en')
    last_updated = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)

class Season(models.Model):
    gsm_id = models.IntegerField()

    competition = models.ForeignKey('Competition')
    name = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from='name_en')

    # tennis specific
    gender = models.CharField(max_length=12, null=True, blank=True)
    prize_money = models.IntegerField(null=True, blank=True)
    prize_currency = models.CharField(max_length=3, null=True, blank=True)
    type = models.CharField(max_length=12, null=True, blank=True)
    
    # soccer specific
    service_level = models.IntegerField(null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)

class Competition(models.Model):
    gsm_id = models.IntegerField()
    display_order = models.IntegerField()

    sport = models.ForeignKey('Sport')
    area = models.ForeignKey('Area')
    championship = models.ForeignKey('Championship', null=True, blank=True)

    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name_en')
    type = models.CharField(max_length=12, null=True, blank=True)
    format = models.CharField(max_length=12, null=True, blank=True)
    soccer_type = models.CharField(max_length=12, null=True, blank=True)
    court_type = models.CharField(max_length=12, null=True, blank=True)
    team_type = models.CharField(max_length=12, null=True, blank=True)
    display_order = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)

class Area(models.Model):
    parent = models.ForeignKey('Area', null=True, blank=True)
    gsm_id = models.IntegerField()
    country_code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name_en')

    def __unicode__(self):
        return self.name
    
    class Meta:
        order_with_respect_to = 'parent'
        ordering = ('-name',)
