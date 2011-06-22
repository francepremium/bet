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

class BetFilter(filters.FilterSet):
    min_date = filters.DateFilter(lookup_type='gte', name='session__datetime_utc')
    max_date = filters.DateFilter(lookup_type='lte', name='session__datetime_utc')
    session__datetime_utc = filters.DateRangeFilter()
    has_text = BetHasTextFilter()
    has_upload = BetHasUploadFilter()

    class Meta:
        model = Bet
        fields = ['ticket__bookmaker', 'bettype', 'session__season__competition', 'session__sport', 'ticket__user']
