# -*- coding: utf-8 -*-
import os.path
import time
import unicodedata
import logging
import re
import unicodedata
import htmlentitydefs
import urllib
import datetime

from django.db.models import Q
from django.db import connection, transaction
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _
from django.core import urlresolvers
from django.template import defaultfilters
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command

from autoslug import AutoSlugField

import gsm

logger = logging.getLogger('gsm')

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

class CachedManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super(CachedManager, self).__init__(*args, **kwargs)
        self.attribute_name = self.get_attribute_name()

    def get_for_object(self, object):
        return self.get_for_pk(getattr(object, self.attribute_name + '_id'))
    
    def get_for_pk(self, pk):
        key = '%s%s' % (self.attribute_name, pk)

        value = cache.get(key)
        if not value:
            value = self.get(pk=pk)
            cache.set(key, value, 99999)
        return value

class AreaManager(CachedManager):
    def get_attribute_name(self):
        return 'area'

    def get_for_pk(self, pk, area=None):
        key = '%s%s' % (self.attribute_name, pk)

        value = cache.get(key)
        if not value:
            if area:
                value = area
            else:
                value = self.get(pk=pk)
            cache.set(key, value, 99999)
        return value

    def get_for_country_code_3(self, code):
        key = '%s%s' % (self.attribute_name, code)
        
        value = cache.get(key)
        area = None
        if not value:
            area = self.get(country_code=code)
            value = area.pk
            cache.set(key, value, 99999)
        return self.get_for_pk(value, area)

    def get_for_country_code_2(self, code):
        key = '%s%s' % (self.attribute_name, code)
        
        value = cache.get(key)
        area = None
        if not value:
            area = self.get(country_code_2=code)
            value = area.pk
            cache.set(key, value, 99999)
        return self.get_for_pk(value, area)

    def get_for_gsm_id(self, code):
        key = '%s%s' % (self.attribute_name, code)

        value = cache.get(key)
        area = None
        if not value:
            area = self.get(gsm_id=code)
            value = area.pk
            cache.set(key, value, 99999)
        return self.get_for_pk(value, area)

class Area(models.Model):
    parent = models.ForeignKey('Area', null=True, blank=True)
    country_code = models.CharField(max_length=3)
    country_code_2 = models.CharField(max_length=2)
    gsm_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    objects = AreaManager()

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)
        order_with_respect_to = 'parent'

class SportManager(CachedManager):
    def get_attribute_name(self):
        return 'sport'

    def get_for_slug(self, code):
        key = '%s%s' % (self.attribute_name, code)

        value = cache.get(key)
        area = None
        if not value:
            area = self.get(slug=code)
            value = area.pk
            cache.set(key, value, 99999)
        return self.get_for_pk(value)

class Sport(models.Model):
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=20)
    fans = models.ManyToManyField('auth.User')

    objects = SportManager()

    def __unicode__(self):
        return _(self.name)
    
    class Meta:
        ordering = ('id',)

    def get_active_competitions(self):
        return self.competition_set.filter(season__session__datetime_utc__gte=datetime.datetime.today()).distinct()

    def get_competition_areas(self):
        return Area.objects.filter(competition__sport=self).order_by('name').distinct()

    def get_absolute_url(self, tab='home'):
        return urlresolvers.reverse('gsm_sport_detail', args=(self.slug,))
    def get_tab_absolute_url(self, tab):
        return urlresolvers.reverse('gsm_sport_detail_tab', args=(self.slug, tab,))
    def get_home_absolute_url(self):
        return self.get_tab_absolute_url('home')
    def get_competitions_absolute_url(self):
        return self.get_tab_absolute_url('competitions')
    def get_informations_absolute_url(self):
        return self.get_tab_absolute_url('informations')
    def get_news_absolute_url(self):
        return self.get_tab_absolute_url('news')
    def get_results_absolute_url(self):
        return self.get_tab_absolute_url('results')
    def get_matches_absolute_url(self):
        return self.get_tab_absolute_url('matches')
    def get_picks_absolute_url(self):
        return self.get_tab_absolute_url('picks')
    def get_live_absolute_url(self):
        return self.get_tab_absolute_url('live')

    def get_last_sessions(self):
        return Session.objects.filter(sport=self, status='Played').order_by('-datetime_utc')[:15]

class AbstractGsmEntity(models.Model):
    sport = models.ForeignKey('Sport')
    gsm_id = models.IntegerField()
    tag = models.CharField(max_length=32, db_index=True)
    area = models.ForeignKey('Area',null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    name_ascii = models.CharField(max_length=150, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    fans = models.ManyToManyField('auth.User')

    class Meta:
        unique_together = ('sport', 'tag', 'gsm_id')
        abstract = True

    def get_sport(self):
        return Sport.objects.get_for_object(self)
    
    def get_tab_absolute_url(self, tab):
        return urlresolvers.reverse('gsm_%s_detail_tab' % self.tag, args=(
            self.get_sport().slug, self.gsm_id, tab))

    def get_home_absolute_url(self):
        return self.get_tab_absolute_url('home')
    def get_file_absolute_url(self):
        return self.get_tab_absolute_url('file')
    def get_squad_absolute_url(self):
        return self.get_tab_absolute_url('squad')
    def get_news_absolute_url(self):
        return self.get_tab_absolute_url('news')
    def get_matches_absolute_url(self):
        return self.get_tab_absolute_url('matches')
    def get_statistics_absolute_url(self):
        return self.get_tab_absolute_url('statistics')
    def get_calendar_absolute_url(self):
        return self.get_tab_absolute_url('calendar')
    def get_picks_absolute_url(self):
        return self.get_tab_absolute_url('picks')

    def get_absolute_url(self):
        try:
            if self.tag == 'match':
                tag = 'session'
            else:
                tag = self.tag
            return urlresolvers.reverse('gsm_%s_detail_tab' % tag, args=(
                self.get_sport().slug, self.gsm_id, 'home'))
        except urlresolvers.NoReverseMatch:
            return urlresolvers.reverse('gsm_entity_detail', args=(
                self.get_sport().slug, self.tag, self.gsm_id,))

    def get_area(self):
        if self.area:
            return self.area

        if not hasattr(self, 'element'):
            return None

        if 'area_id' not in self.element.attrib:
            return None
        else:
            return Area.objects.get_for_gsm_id(int(self.element.attrib['area_id']))

    @property
    def attrib(self):
        """
        Proxy around self.element.attrib
        """
        if not hasattr(self, 'element'):
            return None
        return self.element.attrib


    def __unicode__(self):
        if hasattr(self, 'element'):
            if 'name' in self.attrib.keys():
                return self.attrib['name']
            if 'club_name' in self.attrib.keys():
                return self.attrib['club_name']
            if 'first_name' in self.attrib.keys():
                return '%s %s' % (self.attrib['first_name'], self.attrib['last_name'])
            if 'firstname' in self.attrib.keys():
                return '%s %s' % (self.attrib['firstname'], self.attrib['lastname'])
        return self.name

class GsmEntity(AbstractGsmEntity):
    def get_sessions(self):
        if not hasattr(self, '_sessions'):
            self._sessions = Session.objects.filter(models.Q(oponnent_A=self)|models.Q(oponnent_B=self)).order_by('datetime_utc')
        return self._sessions

    def get_large_image_url(self):
        return self.get_image_url('150x150')

    def get_medium_image_url(self):
        return self.get_image_url('75x75')

    def get_small_image_url(self):
        return self.get_image_url('30x30')

    def get_tiny_image_url(self):
        return self.get_image_url('15x15')

    def get_image_url(self, size):
        tag = self.tag
        ext = 'jpg'
        if tag == 'person':
            tag = 'players'
        elif tag == 'team':
            if self.get_sport().slug == 'soccer':
                return 'http://imagecache.soccerway.com/new/teams/%s/%s.gif' % (size, self.gsm_id)
            elif self.get_sport().slug != 'tennis':
                if self.area:
                    code2 = self.area.country_code_2
                    code3 = self.area.country_code
                elif getattr(self, 'country_code', None):
                    code3 = getattr(self, 'country_code', None)
                    code2 = Area.objects.get_for_country_code_3(code3).country_code_2
                else:
                    return False
                    # debug code
                    raise gsm.CannotFindArea('for self: %s (%s)' % (self, self.__class__))

                code2 = code2.lower()

                if code3 == 'ENG':
                    code2 = '_England'
                elif code3 == 'SCO':
                    code2 = '_Scotland'
                elif code3 == 'WAL':
                    code2 = '_Wales'

                if size == '15x15':
                    height = 16
                elif size == '30x30':
                    height = 24
                elif size in ('75x75', '150x150'):
                    height = 48

                return '%sflags2/%s/%s.png' % (
                    settings.STATIC_URL,
                    height,
                    code2
                )

        return 'http://images.globalsportsmedia.com/%s/%s/%s/%s.%s' % (
            self.get_sport().slug, tag, size, self.gsm_id, ext)

    def is_nationnal(self):
        return Competition.objects.filter(
                    Q(season__session__oponnent_A=self)|
                    Q(season__session__oponnent_B=self)).filter(
                        area=Area.objects.get_for_pk(1)).count() > 0

    def oponnent_A_name(self):
        raise Exception('oponnent_A_name has been deprecated. Use oponnent_A.name instead')
    def oponnent_B_name(self):
        raise Exception('oponnent_B_name has been deprecated. Use oponnent_B.name instead')

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

    important = models.BooleanField()

    def get_sessions(self):
        return Session.objects.filter(session_round__season__competition=self).order_by('-datetime_utc')

    def get_last_season(self):
        if not hasattr(self, '_last_season'):
            self._last_season = self.season_set.all().order_by('-end_date')[0]
        return self._last_season

    def __unicode__(self):
        if self.name:
            return self.name
        if hasattr(self, 'element'):
            return self.attrib.name
        return super(Competition, self).__unicode__()

class Season(AbstractGsmEntity):
    competition = models.ForeignKey('Competition')

    # tennis specific
    gender = models.CharField(max_length=12, null=True, blank=True)
    prize_money = models.IntegerField(null=True, blank=True)
    prize_currency = models.CharField(max_length=3, null=True, blank=True)
    # type is a reserved word
    season_type = models.CharField(max_length=20, null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def get_gameweeks(self):
        if not hasattr(self, '_gameweeks'):
            self._gameweeks = []
            sql = 'select distinct on (gameweek) gameweek, datetime_utc from gsm_session where season_id = %s'
            cursor = connection.cursor()
            cursor.execute(sql, (self.pk,))
            self._gameweeks = cursor.fetchall()
        return self._gameweeks

    def get_last_gameweek(self):
        if not hasattr(self, '_last_gameweek'):
            self._last_gameweek = int(self.get_gameweeks()[-1][0])
        return self._last_gameweek

    def get_current_gameweek(self):
        if not hasattr(self, '_current_gameweek'):
            sessions = self.session_set.filter(status='Fixture', datetime_utc__gte=datetime.date.today()).order_by('datetime_utc')
            if sessions.count() and sessions[0].gameweek:
                self._current_gameweek = int(sessions[0].gameweek)
            else:
                self._current_gameweek = False
        return self._current_gameweek

    def get_current_round(self):
        if not hasattr(self, '_current_round'):
            next_rounds = self.round_set.filter(end_date__gte=datetime.date.today()).order_by('-end_date')
            if next_rounds.count():
                self._current_round = next_rounds[0]
            else:
                self._current_round = self.round_set.order_by('-end_date', '-gsm_id')[0]

        return self._current_round

    def get_sessions_for_current_gameweek(self):
        if not hasattr(self, '_sessions_for_current_gameweek'):
            self._sessions_for_current_gameweek = self.session_set.filter(gameweek=self.get_current_gameweek).order_by('datetime_utc')
        return self._sessions_for_current_gameweek

class Round(AbstractGsmEntity):
    season = models.ForeignKey('Season')

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # type is a reserved word
    round_type = models.CharField(max_length=12, null=True, blank=True)
    scoring_system = models.CharField(max_length=12, null=True, blank=True)
    groups = models.IntegerField()
    has_outgroup_matches = models.BooleanField()

    def get_previous_round(self):
        if not hasattr(self, '_previous_round'):
            previous_rounds = Round.objects.filter(start_date__lt=self.start_date, season=self.season).order_by('-start_date')
            if previous_rounds.count():
                self._previous_round = previous_rounds[0]
            else:
                self._previous_round = False
        return self._previous_round

    def get_next_round(self):
        if not hasattr(self, '_next_round'):
            next_rounds = Round.objects.filter(start_date__gt=self.start_date, season=self.season).order_by('start_date')
            if next_rounds.count():
                self._next_round = next_rounds[0]
            else:
                self._next_round = False
        return self._next_round

class SessionManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        """
        Optimize for current templates/gsm/_includes/sessions.html
        """
        q = super(SessionManager, self).get_query_set()
        q = q.select_related('oponnent_A', 'oponnent_B', 'session_round', 
            'session_round__season', 'session_round__season__competition', 
            'session_round__season__competition__area', 'sport', 'oponnent_A')
        return q


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
    A5_score = models.IntegerField(null=True, blank=True)
    B1_score = models.IntegerField(null=True, blank=True)
    B2_score = models.IntegerField(null=True, blank=True)
    B3_score = models.IntegerField(null=True, blank=True)
    B4_score = models.IntegerField(null=True, blank=True)
    B5_score = models.IntegerField(null=True, blank=True)

    # soccer, rugby
    A_score = models.IntegerField(null=True, blank=True)
    B_score = models.IntegerField(null=True, blank=True)
    A_ets = models.IntegerField(null=True, blank=True)
    B_ets = models.IntegerField(null=True, blank=True)
    penalty = models.CharField(null=True, blank=True, max_length=1)

    actual_start_datetime = models.DateTimeField(null=True, blank=True)
    datetime_utc = models.DateTimeField(null=True, blank=True)
    time_unknown = models.BooleanField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    gameweek = models.IntegerField(null=True, blank=True)

    winner = models.ForeignKey('GsmEntity', null=True, blank=True, related_name='won_sessions')
    oponnent_A = models.ForeignKey('GsmEntity', related_name='sessions_as_A', null=True, blank=True)
    oponnent_B = models.ForeignKey('GsmEntity', related_name='sessions_as_B', null=True, blank=True)

    objects = SessionManager()

    class Meta:
        ordering = ['datetime_utc']

    def __unicode__(self):
        return self.name

    def get_tab_absolute_url(self, tab):
        return urlresolvers.reverse('gsm_%s_detail_tab' % 'session', args=(
            self.get_sport().slug, self.gsm_id, tab))
    
    def get_after_absolute_url(self):
        return self.get_tab_absolute_url('after')
    def get_live_absolute_url(self):
        return self.get_tab_absolute_url('live')

def ensure_ascii_name(sender, **kwargs):
    model = kwargs.pop('instance')
    for code, language in settings.LANGUAGES:
        if hasattr(model, 'name_ascii_%s' % code):
            name = getattr(model, 'name_%s' % code, False)
            if name:
                name_ascii = unicodedata.normalize(
                    'NFKD', name).encode('ascii','ignore')
                setattr(model, 'name_ascii_%s' % code, name_ascii)
signals.pre_save.connect(ensure_ascii_name)
