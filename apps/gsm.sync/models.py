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
        ordering = ('id',)

class GsmEntity(models.Model):
    gsm_id = models.IntegerField()
    sport = models.ForeignKey('Sport')

    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')
    last_updated = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)
        abstract = True
        unique_together = ('gsm_id', 'sport')

class Area(models.Model):
    parent = models.ForeignKey('Area', null=True, blank=True)
    country_code = models.CharField(max_length=3)
    gsm_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='name_en')

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('-name',)
        order_with_respect_to = 'parent'

class Championship(GsmEntity):
    pass

class Competition(GsmEntity):
    display_order = models.IntegerField()
    
    area = models.ForeignKey('Area')
    championship = models.ForeignKey('Championship', null=True, blank=True)

    # type and format are reserved words
    competition_type = models.CharField(max_length=32, null=True, blank=True)
    competition_format = models.CharField(max_length=32, null=True, blank=True)
    court_type = models.CharField(max_length=12, null=True, blank=True)
    team_type = models.CharField(max_length=12, null=True, blank=True)
    display_order = models.IntegerField(null=True, blank=True)

class Season(GsmEntity):
    competition = models.ForeignKey('Competition')

    # tennis specific
    gender = models.CharField(max_length=12, null=True, blank=True)
    prize_money = models.IntegerField(null=True, blank=True)
    prize_currency = models.CharField(max_length=3, null=True, blank=True)
    # type is a reserved word
    season_type = models.CharField(max_length=12, null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

class Round(GsmEntity):
    season = models.ForeignKey('Season')

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # type is a reserved word
    round_type = models.CharField(max_length=12, null=True, blank=True)
    scoring_system = models.CharField(max_length=12, null=True, blank=True)
    groups = models.IntegerField()
    has_outgroup_matches = models.BooleanField()

class Session(GsmEntity):
    STATUS_CHOICES = (
        ('Played', _(u'match has been played')),
        ('Playing', _(u'match is playing (live)')),
        ('Fixture', _(u'match is scheduled')),
        ('Cancelled', _(u'match is postponed to other (unknown) date')),
        ('Postponed', _(u'match is cancelled and won\'t be played again')),
        ('Suspended', _(u'match is suspended during match')),
    )

    datetime_utc = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    gameweek = models.IntegerField()
    season = models.ForeignKey('Season', null=True, blank=True)
    session_round = models.ForeignKey('Round', null=True, blank=True)
    
    # ball games
    winner_team = models.ForeignKey('Team', null=True, blank=True, related_name='sessions_won')
    team_A = models.ForeignKey('Team', null=True, blank=True, related_name='sessions_A')
    team_B = models.ForeignKey('Team', null=True, blank=True, related_name='sessions_B')
    ets_A = models.IntegerField(verbose_name=_(u'extra time score of team A'), null=True, blank=True, help_text=_(u'Extra-time score, available when match gets into overtime.'))
    ets_B = models.IntegerField(verbose_name=_(u'extra time score of team B'), null=True, blank=True, help_text=_(u'Extra-time score, available when match gets into overtime.'))
    fs_A = models.IntegerField(verbose_name=_(u'full time score of team A'), null=True, blank=True, help_text=_(u'Full-time score represents result after regular time (90 minutes) when match status is played.'))
    fs_B = models.IntegerField(verbose_name=_(u'full time score of team B'), null=True, blank=True, help_text=_(u'Full-time score represents result after regular time (90 minutes) when match status is played.'))
    hts_A = models.IntegerField(verbose_name=_(u'half time score of team A'), null=True, blank=True, help_text=_(u'Half-time score is available as soon as first half ends.'))
    hts_B = models.IntegerField(verbose_name=_(u'half time score of team B'), null=True, blank=True, help_text=_(u'Half-time score is available as soon as first half ends.'))

    # soccer specific
    ps_A = models.IntegerField(verbose_name=_(u'Score made in penalty shootout by team A'), null=True, blank=True, help_text=_(u'Score made in penalty shootout, usually when overtime ended with draw. Updated live.'))
    ps_B = models.IntegerField(verbose_name=_(u'Score made in penalty shootout by team B'), null=True, blank=True, help_text=_(u'Score made in penalty shootout, usually when overtime ended with draw. Updated live.'))

    # tennis specific
    actual_start_datetime = models.DateTimeField(null=True, blank=True)
    person_A = models.ForeignKey('Person', null=True, blank=True, related_name='sessions_A')
    person_B = models.ForeignKey('Person', null=True, blank=True, related_name='sessions_B')
    score_A = models.IntegerField(null=True, blank=True)
    score_B = models.IntegerField(null=True, blank=True)

class TennisSet(models.Model):
    pass

class Person(GsmEntity):
    area = models.ForeignKey('Area')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    person_type = models.CharField(max_length=12)
    gender = models.CharField(max_length=12)
    birth = models.DateField(null=True, blank=True)

class Team(GsmEntity):
    area = models.ForeignKey('Area')

    team_type = models.CharField(max_length=18, null=True, blank=True)
    play_type = models.CharField(max_length=18, null=True, blank=True)
    official_name = models.CharField(max_length=60, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    colors = models.CharField(max_length=100, null=True, blank=True)
    clothing = models.CharField(max_length=100, null=True, blank=True)
    sponsor = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField()
