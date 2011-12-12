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
import django.dispatch
import pytz
from pytz import timezone
from django.db.models import Max

from autoslug import AutoSlugField

import gsm

session_played = django.dispatch.Signal(providing_args=['session'])

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
        key = '%spk%s' % (self.attribute_name, pk)

        value = cache.get(key)
        if not value:
            if area:
                value = area
            else:
                value = self.get(pk=pk)
            cache.set(key, value, 99999)
        return value

    def get_for_country_code_3(self, code):
        key = '%scc3%s' % (self.attribute_name, code)
        
        value = cache.get(key)
        area = None
        if not value:
            area = self.get(country_code=code)
            value = area.pk
            cache.set(key, value, 99999)
        return self.get_for_pk(value, area)

    def get_for_country_code_2(self, code):
        key = '%scc2%s' % (self.attribute_name, code)
        
        value = cache.get(key)
        area = None
        if not value:
            area = self.get(country_code_2=code)
            value = area.pk
            cache.set(key, value, 99999)
        return self.get_for_pk(value, area)

    def get_for_gsm_id(self, code):
        key = '%sgsmid%s' % (self.attribute_name, code)

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
        return self.competition_set.filter(season__session__start_datetime__gte=datetime.datetime.today()).distinct()

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
    def get_matches_absolute_url(self):
        return self.get_tab_absolute_url('matches')
    def get_picks_absolute_url(self):
        return self.get_tab_absolute_url('picks')
    def get_rankings_absolute_url(self):
        return self.get_tab_absolute_url('rankings')

    def get_last_sessions(self):
        return Session.objects.filter(sport=self, status='Played').order_by('-start_datetime')[:15]

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
    def get_rankings_absolute_url(self):
        return self.get_tab_absolute_url('rankings')

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


    def get_datetime(self, el, date_attr, time_attr):
        datetime_str = '%s %s' % (
            el.attrib.get(date_attr, False) or '',
            el.attrib.get(time_attr, False) or '00:00:00',
        )

        if datetime_str[-1] == ' ': # no time, set to midnight
            datetime_str = datetime_str + '00:00:00'

        if datetime_str not in (' ', ' 00:00:00'):
            converter = Session._meta.get_field('start_datetime')
            return converter.to_python(datetime_str)

    def resync(self, element=None):
        if not element:
            tree = gsm.get_tree('en', self.sport, 'get_matches', 
                type='match', id=self.gsm_id, update=True, retry=True)
            for e in gsm.parse_element_for(tree.getroot(), 'match'):
                element = e

        s = Sync(self.sport, False, False, False)
        s.update(e)

class GsmEntity(AbstractGsmEntity):
    def get_sessions(self):
        if not hasattr(self, '_sessions'):
            self._sessions = Session.objects.filter(models.Q(oponnent_A=self)|models.Q(oponnent_B=self)).order_by('start_datetime')
        return self._sessions

    def get_large_image_url(self):
        return self.get_image_url('150x150')

    def get_medium_image_url(self):
        return self.get_image_url('75x75')

    def get_small_image_url(self):
        return self.get_image_url('50x50')

    def get_extra_small_image_url(self):
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
            elif self.get_sport().slug == 'rugby':
                tag = 'teams'
                ext = 'png'
                if size not in ('75x75', '150x150'):
                    size = '75x75'
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

    def has_squad(self):
        if not hasattr(self, '_has_squad'):
            tree = gsm.get_tree('en', self.sport,
                'get_squads', type='team', id=self.gsm_id, detailed='yes',
                statistics='yes')
            self._has_squad = len(tree.findall('team')) > 0
        return self._has_squad


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
        return Session.objects.filter(session_round__season__competition=self).order_by('-start_datetime')

    def get_last_season(self):
        if not hasattr(self, '_last_season'):
            self._last_season = self.season_set.all().order_by('-start_date')[0]
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
            sql = 'select distinct on (gameweek) gameweek, start_datetime from gsm_session where season_id = %s'
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
            sessions = self.session_set.filter(status='Fixture', start_datetime__gte=datetime.date.today()).order_by('start_datetime')
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
            self._sessions_for_current_gameweek = self.session_set.filter(gameweek=self.get_current_gameweek).order_by('start_datetime')
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
    start_datetime = models.DateTimeField(null=True, blank=True)
    time_unknown = models.BooleanField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    gameweek = models.IntegerField(null=True, blank=True)

    winner = models.ForeignKey('GsmEntity', null=True, blank=True, related_name='won_sessions')
    oponnent_A = models.ForeignKey('GsmEntity', related_name='sessions_as_A', null=True, blank=True)
    oponnent_B = models.ForeignKey('GsmEntity', related_name='sessions_as_B', null=True, blank=True)

    objects = SessionManager()

    class Meta:
        ordering = ['start_datetime']

    def __unicode__(self):
        return self.name

    def get_tab_absolute_url(self, tab):
        return urlresolvers.reverse('gsm_%s_detail_tab' % 'session', args=(
            self.get_sport().slug, self.gsm_id, tab))

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

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
local = timezone(settings.TIME_ZONE)
london = timezone('Europe/London')

def datetime_to_string(dt):
    return dt.strftime(DATETIME_FORMAT)

def string_to_datetime(s):
    if s == '0000-00-00 00:00:00':
        return

    try:
        return datetime.datetime.strptime(s, DATETIME_FORMAT)
    except ValueError:
        return datetime.datetime.strptime(s, '%Y-%m-%d')

class Sync(object):
    def __init__(self, sport, last_updated, minimal_date, logger, 
        cooldown=0, language='en', names_only=False, quiet=False):
        self.sport = sport
        self.minimal_date = minimal_date
        self.language = language
        self.logger = logger
        self.cooldown = cooldown
        self.names_only = names_only
        self.quiet = quiet

        if isinstance(last_updated, str):
            self.last_updated = string_to_datetime(last_updated)
        else:
            self.last_updated = last_updated
        if self.last_updated and not self.last_updated.tzinfo:
            self.last_updated = local.localize(self.last_updated)

        if self.minimal_date and not self.minimal_date.tzinfo:
            self.minimal_date = local.localize(self.minimal_date)

        if self.sport.slug == 'tennis':
            self.oponnent_tag = 'person'
        else:
            self.oponnent_tag = 'team'

        self.autocopy = (
            'start_date',
            'end_date'
        )

        self._tag_class_map = {
            'competition': Competition,
            'tour': Championship,
            'season': Season,
            'match': Session,
        }

        self._tag_method_map = {
            'competition': 'get_competitions',
            'tour': 'get_tours',
            'season': 'get_seasons',
            'match': 'get_matches',
        }

    def log(self, level, message):
        if not self.quiet:
            message = u'[%s] ' % self.sport.slug + message.decode('utf-8')
            if self.logger:
                self.logger.log(getattr(logging, level.upper()), message)
            else:
                print '[%s] %s' % (level.upper(), message)

    def get_tree(self, *args, **kwargs):
        kwargs['retry'] = 3000
        kwargs['update'] = True

        for k, v in kwargs.items():
            if isinstance(v, datetime.datetime):
                kwargs[k] = datetime_to_string(v.astimezone(london))

        return gsm.get_tree(self.language, self.sport, *args, **kwargs
            ).getroot()

    def skip(self, e):
        if e.tag not in self._tag_class_map.keys():
            self.log('debug', 'Skipping tag %s' % e.tag)
            return True

        last_updated = string_to_datetime(e.attrib['last_updated'])
        if last_updated:
            last_updated = london.localize(last_updated)
            if self.last_updated and last_updated < self.last_updated:
                self.log('debug', 'Skipping because no update %s #%s' % (e.tag, 
                    e.attrib.get('%s_id' % e.tag)))
                return True
        
        date_attrs = [
            'start_date',
            'end_date',
        ]

        date = None
        for key in date_attrs:
            try:
                date = e.attrib.get(key)
                break
            except:
                continue

        if date:
            date = string_to_datetime(date)
            date = london.localize(date)
            if self.minimal_date and date < self.minimal_date:
                self.log('debug', 'Skipping too old %s #%s' % (e.tag,
                    e.attrib.get('%s_id' % e.tag)))
                return True

        self.log('debug', 'Update necessary for %s #%s' % (e.tag,
            e.attrib.get('%s_id' % e.tag)))

    def element_to_model(self, e):
        try:
            return self._tag_class_map[e.tag].objects.get(
                sport=self.sport, gsm_id=e.attrib[e.tag + '_id'],
                tag=e.tag)
        except self._tag_class_map[e.tag].DoesNotExist:
            return self._tag_class_map[e.tag](
                sport=self.sport, gsm_id=e.attrib[e.tag + '_id'],
                tag=e.tag)

    def set_model_area(self, model, e):
        if not hasattr(model, 'area'):
            return

        if 'area_id' not in e.attrib.keys():
            return

        model.area = Area.objects.get_for_gsm_id(e.attrib['area_id'])

    def set_model_name(self, model, e):
        if 'name' in e.attrib.keys():
            setattr(model, 'name_%s' %  self.language, 
                unicode(e.attrib['name']))

        elif isinstance(model, Session):
            names = []
            for X in ('A', 'B'):
                names.append(unicode(
                    e.attrib['%s_%s_name' % (self.oponnent_tag, X)]))

            setattr(model, 'name_%s' %  self.language, u' vs. '.join(names))

        else:
            raise gsm.GsmException(
                'Cannot find name for sport %s tag %s gsm_id %s' % (
                self.sport.slug, model.tag, model.gsm_id))

    def update(self, e, parent=None):
        model = self.element_to_model(e)
        self.log('debug', 'Updating %s:%s' % (model.tag, model.gsm_id))

        self.set_model_name(model, e)

        if not self.names_only:
            self.set_model_area(model, e)

            for key in self.autocopy:
                if key in e.attrib.keys() and hasattr(model, key):
                    self.copy_attr(model, e, key)

            method_key = model.__class__.__name__.lower()
            method = 'update_%s' % method_key
            if hasattr(self, method):
                getattr(self, method)(model, e, parent)

            method = 'update_%s_%s' % (self.sport.slug, method_key)
            if hasattr(self, method):
                getattr(self, method)(model, e, parent)
        model.save()

        def update_children(e):
            for child in e.getchildren():
                if 'double_A_id' in e.attrib.keys():
                    continue # important !!

                if self.skip(child):
                    update_children(child)
                else:
                    self.update(child, parent=model)
        update_children(e)

        if e.tag == 'season':
            tree = self.get_tree('get_matches', type='season', id=model.gsm_id, detailed='yes')
            for sube in gsm.parse_element_for(tree, 'match'):
                if not self.skip(sube):
                    if 'double_A_id' in sube.attrib.keys():
                        continue # important !!
                    self.update(sube, model)

        time.sleep(self.cooldown)

    def copy_attr(self, model, e, source, destination=None):
        if destination is None:
            destination = source
        
        value = e.attrib.get(source, None) or None

        if unicode(value) == u'4294967295':
            # gsm screwd up again
            return

        setattr(model, destination, value)

    def update_competition(self, model, e, parent=None):
        model.championship = parent

        self.copy_attr(model, e, 'court', 'court_type')
        self.copy_attr(model, e, 'teamtype', 'team_type')
        self.copy_attr(model, e, 'type', 'competition_type')
        self.copy_attr(model, e, 'format', 'competition_format')

        if not model.display_order:
            model.display_order = Competition.objects.filter(sport=self.sport
                ).aggregate(Max('display_order'))['display_order__max'] or 0 + 1
    
    def update_season(self, model, e, parent=None):
        model.competition = parent

        self.copy_attr(model, e, 'type', 'season_type')
        self.copy_attr(model, e, 'gender')
        self.copy_attr(model, e, 'prize_money')
        self.copy_attr(model, e, 'prize_currency')
    
    def update_session(self, model, e, parent=None):
        if isinstance(parent, Round):
            model.round = parent
            model.season = parent.season
        elif isinstance(parent, Season):
            model.season = parent

        model.start_datetime = self.get_session_start_datetime(e)

        old_status = model.status
        self.copy_attr(model, e, 'status')
        if model.status != old_status:
            session_played.send(sender=self, session=model)
        
        self.copy_attr(model, e, 'gameweek')

        P = self.oponnent_tag
        for X in ('A', 'B'):
            self.copy_attr(model, e, 'fs_%s' % X, '%s_score' % X)
            self.copy_attr(model, e, 'eps_%s' % X, '%s_ets' % X)
            self.copy_attr(model, e, 'ets_%s' % X, '%s_ets' % X)
            self.copy_attr(model, e, 'p1s_%s' % X, '%s1_score' % X)
            self.copy_attr(model, e, 'p2s_%s' % X, '%s2_score' % X)
            self.copy_attr(model, e, 'p3s_%s' % X, '%s3_score' % X)
            self.copy_attr(model, e, 'p4s_%s' % X, '%s4_score' % X)

            if e.attrib['%s_%s_id' % (P, X)]:
                oponnent, created = GsmEntity.objects.get_or_create(
                    sport=self.sport,
                    gsm_id=e.attrib['%s_%s_id' % (P, X)],
                    tag=self.oponnent_tag)

                if created:
                    code = e.attrib.get('%s_%s_country' % (P, X))
                    oponnent.area = Area.objects.get_for_country_code_3(code)
                    self.copy_attr(oponnent, e, '%s_%s_name' % (P, X), 'name')

                setattr(model, 'oponnent_%s' % X, oponnent)

        winner = e.attrib.get('winner', None)
        if 'A' in winner:
            model.winner = model.oponnent_A
        elif 'B' in winner:
            model.winner = model.oponnent_B
        elif winner == 'draw':
            model.draw = True

    def update_tennis_session(self, model, e, parent=None):
        i = 1
        for set_element in e.findall('set'):
            for X in ('A', 'B'):
                self.copy_attr(model, set_element, 'score_%s' % X, 
                    '%s%s_score' % (X, i))

            i += 1
            if i > 5:
                break

    def update_soccer_session(self, model, e, parent=None):
        ps_A = e.attrib.get('ps_A', '')
        ps_B = e.attrib.get('ps_B', '')
        if ps_A:
            if ps_A > ps_B:
                model.penalty = 'A'
            else:
                model.penalty = 'B'

    def update_rugby_session(self, model, e, parent=None):
        ps_A = e.attrib.get('sds_A', '')
        ps_B = e.attrib.get('sds_B', '')
        if ps_A:
            if ps_A > ps_B:
                model.penalty = 'A'
            else:
                model.penalty = 'B'
    
    def get_session_start_datetime(self, e):
        # Welcome to GSM's vision of hell
        converter = Session._meta.get_field('actual_start_datetime')
        actual_start_datetime = '%s %s' % (
            e.attrib.get('actual_start_date', '') or '',
            e.attrib.get('actual_start_time', '') or '',
        )
        
        if actual_start_datetime[-1] == ' ': # no time, set to midnight
            actual_start_datetime = actual_start_datetime + '00:00:00'

        if actual_start_datetime not in (' ', ' 00:00:00'):
            actual_start_datetime = converter.to_python(actual_start_datetime)
        else:
            actual_start_datetime = None

        if 'official_start_date' in e.attrib.keys():
            official_start_datetime = '%s %s' % (
                e.attrib.get('official_start_date', '') or '',
                e.attrib.get('official_start_time', '00:00:00') or '00:00:00',
            )
        else:
            official_start_datetime = '%s %s' % (
                e.attrib.get('date_london', '') or '',
                e.attrib.get('time_london', '00:00:00') or '00:00:00',
            )

        if official_start_datetime[-1] == ' ': # no time, set to midnight
            official_start_datetime = official_start_datetime + '00:00:00'
        if official_start_datetime not in (' ', ' 00:00:00'):
            official_start_datetime = converter.to_python(official_start_datetime)
        else:
            official_start_datetime = None

        dt = actual_start_datetime or official_start_datetime
        dt = london.localize(dt)

        return dt
