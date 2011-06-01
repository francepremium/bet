import datetime

from django import forms
from django.utils.translation import ugettext as _

import django_filters

from models import *

class BetHasTextFilter(django_filters.BooleanFilter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value is not False:
            return qs.exclude(text='')
        return qs

class BetHasUploadFilter(django_filters.BooleanFilter):
    field_class = forms.BooleanField

    def filter(self, qs, value):
        if value is not False:
            return qs.exclude(upload='')
        return qs

class BetFilter(django_filters.FilterSet):
    min_date = django_filters.DateFilter(lookup_type='gte', name='session__datetime_utc')
    max_date = django_filters.DateFilter(lookup_type='lte', name='session__datetime_utc')
    session__datetime_utc = django_filters.DateRangeFilter()
    has_text = BetHasTextFilter()
    has_upload = BetHasUploadFilter()

    class Meta:
        model = Bet
        fields = ['ticket__bookmaker', 'bettype', 'session__season__competition', 'session__sport', 'ticket__user']
