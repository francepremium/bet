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

import gsm

class GsmEntityNoLanguageException(gsm.GsmException):
    pass

def model_class_for_tag(tag):
    if tag in ('tour', 'championship'):
        return Championship
    if tag in ('competition',):
        return Competition
    if tag in ('season',):
        return Season
    if tag in ('round',):
        return Round
    if tag in ('session', 'match',):
        return Session
    return GsmEntity

class Area(models.Model):
    parent = models.ForeignKey('Area', null=True, blank=True)
    country_code = models.CharField(max_length=3)
    gsm_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)
        order_with_respect_to = 'parent'

class Sport(models.Model):
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=20)

    def __unicode__(self):
        return _(self.name)
    
    class Meta:
        ordering = ('id',)

    def get_absolute_url(self, tab):
        return urlresolvers.reverse('gsm_sport_detail', args=(self.slug,))
    def get_tab_absolute_url(self, tab):
        return urlresolvers.reverse('gsm_sport_detail_tab', args=(self.slug, tab,))
    def get_home_absolute_url(self):
        return self.get_tab_absolute_url('home')
    def get_informations_absolute_url(self):
        return self.get_tab_absolute_url('informations')
    def get_news_absolute_url(self):
        return self.get_tab_absolute_url('news')
    def get_results_absolute_url(self):
        return self.get_tab_absolute_url('results')
    def get_matches_absolute_url(self):
        return self.get_tab_absolute_url('matches')
    def get_prognostics_absolute_url(self):
        return self.get_tab_absolute_url('prognostics')
    def get_live_absolute_url(self):
        return self.get_tab_absolute_url('live')

    def get_last_sessions(self):
        return Session.objects.filter(sport=self, status='Played').order_by('-datetime_utc')[:15]

class AbstractGsmEntity(models.Model):
    sport = models.ForeignKey('Sport')
    gsm_id = models.IntegerField()
    tag = models.CharField(max_length=32)
    area = models.ForeignKey('Area',null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('sport', 'tag', 'gsm_id')
        abstract = True

    def get_tab_absolute_url(self, tab):
        return urlresolvers.reverse('gsm_%s_detail_tab' % self.tag, args=(
            self.sport, self.gsm_id, tab))

    def get_home_absolute_url(self):
        return self.get_tab_absolute_url('home')
    def get_file_absolute_url(self):
        return self.get_tab_absolute_url('file')
    def get_squad_absolute_url(self):
        return self.get_tab_absolute_url('squad')
    def get_news_absolute_url(self):
        return self.get_tab_absolute_url('news')
    def get_statistics_absolute_url(self):
        return self.get_tab_absolute_url('statistics')
    def get_calendar_absolute_url(self):
        return self.get_tab_absolute_url('calendar')
    def get_prognostics_absolute_url(self):
        return self.get_tab_absolute_url('prognostics')

    def get_absolute_url(self):
        try:
            return urlresolvers.reverse('gsm_%s_detail' % self.tag, args=(
                self.sport, self.gsm_id, ))
        except urlresolvers.NoReverseMatch:
            return urlresolvers.reverse('gsm_entity_detail', args=(
                self.sport, self.tag, self.gsm_id,))

    def get_area(self):
        if self.area:
            return self.area

        if not hasattr(self, 'element'):
            return None

        if 'area_id' not in self.element.attrib:
            return None
        else:
            return Area.objects.get(gsm_id = self.element.attrib['area_id'])

    @property
    def attrib(self):
        """
        Proxy around self.element.attrib
        """
        if not hasattr(self, 'element'):
            return None
        return self.element.attrib


    def __unicode__(self):
        return '%s (<%s> #%s %s)' % (self.name, self.tag, self.gsm_id, self.sport)

class GsmEntity(AbstractGsmEntity):
    pass

class Championship(AbstractGsmEntity):
    pass

class Competition(AbstractGsmEntity):
    display_order = models.IntegerField()
    
    championship = models.ForeignKey('Championship', null=True, blank=True)

    # type and format are reserved words
    competition_type = models.CharField(max_length=32, null=True, blank=True)
    competition_format = models.CharField(max_length=32, null=True, blank=True)
    court_type = models.CharField(max_length=12, null=True, blank=True)
    team_type = models.CharField(max_length=12, null=True, blank=True)
    display_order = models.IntegerField(null=True, blank=True)

    def get_sessions(self):
        return Session.objects.filter(session_round__season__competition=self).order_by('-datetime_utc')

class Season(AbstractGsmEntity):
    competition = models.ForeignKey('Competition')

    # tennis specific
    gender = models.CharField(max_length=12, null=True, blank=True)
    prize_money = models.IntegerField(null=True, blank=True)
    prize_currency = models.CharField(max_length=3, null=True, blank=True)
    # type is a reserved word
    season_type = models.CharField(max_length=12, null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

class Round(AbstractGsmEntity):
    season = models.ForeignKey('Season')

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # type is a reserved word
    round_type = models.CharField(max_length=12, null=True, blank=True)
    scoring_system = models.CharField(max_length=12, null=True, blank=True)
    groups = models.IntegerField()
    has_outgroup_matches = models.BooleanField()

class Session(AbstractGsmEntity):
    season = models.ForeignKey('Season', null=True, blank=True)
    session_round = models.ForeignKey('Round', null=True, blank=True)

    STATUS_CHOICES = (
        ('Played', _(u'match has been played')),
        ('Playing', _(u'match is playing (live)')),
        ('Fixture', _(u'match is scheduled')),
        ('Cancelled', _(u'match is postponed to other (unknown) date')),
        ('Postponed', _(u'match is cancelled and won\'t be played again')),
        ('Suspended', _(u'match is suspended during match')),
    )

    draw = models.NullBooleanField(null=True, blank=True)

    # tennis, basket
    A1_score = models.IntegerField(null=True, blank=True)
    A2_score = models.IntegerField(null=True, blank=True)
    A3_score = models.IntegerField(null=True, blank=True)
    A4_score = models.IntegerField(null=True, blank=True)
    AE_score = models.IntegerField(null=True, blank=True)
    B1_score = models.IntegerField(null=True, blank=True)
    B2_score = models.IntegerField(null=True, blank=True)
    B3_score = models.IntegerField(null=True, blank=True)
    B4_score = models.IntegerField(null=True, blank=True)
    BE_score = models.IntegerField(null=True, blank=True)

    # soccer, rugby
    A_score = models.IntegerField(null=True, blank=True)
    B_score = models.IntegerField(null=True, blank=True)
    A_ets = models.IntegerField(null=True, blank=True)
    B_ets = models.IntegerField(null=True, blank=True)
    penalty = models.CharField(null=True, blank=True, max_length=1)

    actual_start_datetime = models.DateTimeField(null=True, blank=True)
    datetime_utc = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    gameweek = models.IntegerField(null=True, blank=True)

    winner = models.ForeignKey('GsmEntity', null=True, blank=True, related_name='won_sessions')
    oponnent_A = models.ForeignKey('GsmEntity', related_name='sessions_as_A', null=True, blank=True)
    oponnent_B = models.ForeignKey('GsmEntity', related_name='sessions_as_B', null=True, blank=True)
    oponnent_A_name = models.CharField(max_length=60, null=True, blank=True)
    oponnent_B_name = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        ordering = ['-datetime_utc']
