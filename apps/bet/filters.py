import datetime

from django import forms
from django.utils.translation import ugettext as _

import django_filters as filters

from models import *

class BetHasTextFilter(filters.BooleanFilter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value is not False:
            return qs.exclude(text='')
        return qs

class BetHasUploadFilter(filters.BooleanFilter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value is not False:
            return qs.exclude(upload='')
        return qs

class PopulationChoiceFilter(filters.ChoiceFilter):
    def filter(self, qs, value):
        if value == 'friends':
            return qs.filter(ticket__user__in=self.user.friends())
        elif value == 'follow':
            return qs.filter(ticket__user__in=self.user.following())
        else:
            return qs

class BetFilter(filters.FilterSet):
    POPULATION_CHOICES = (
        ('all', _('all')),
        ('friends', _('friends')),
        ('follow', _('who I follow')),
    )
    min_date = filters.DateFilter(lookup_type='gte', name='session__datetime_utc')
    max_date = filters.DateFilter(lookup_type='lte', name='session__datetime_utc')
    session__datetime_utc = filters.DateRangeFilter()
    has_text = BetHasTextFilter()
    has_upload = BetHasUploadFilter()
    population = PopulationChoiceFilter(choices=POPULATION_CHOICES)

    class Meta:
        model = Bet
        fields = ['ticket__bookmaker', 'bettype', 'session__season__competition', 'session__sport']
