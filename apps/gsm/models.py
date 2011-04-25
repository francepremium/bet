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
    gsm_name = models.CharField(max_length=30, editable=False)

    def __unicode__(self):
        return self.gsm_name
    
    class Meta:
        ordering = ('-gsm_name',)

class Area(models.Model):
    parent = models.ForeignKey('Area', null=True, blank=True, editable=False)
    gsm_id = models.IntegerField(editable=False)
    gsm_country_code = models.CharField(max_length=3, editable=False)
    gsm_name = models.CharField(max_length=100, editable=False)

    def __unicode__(self):
        return self.gsm_name
    
    class Meta:
        order_with_respect_to = 'parent'
        ordering = ('-name',)
