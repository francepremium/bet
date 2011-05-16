import datetime

from django.utils.translation import ugettext as _

import django_filters

from models import *

class DummyChoiceFilter(django_filters.ChoiceFilter):
    def filter(self, qs, value):
        return qs

class SessionFilter(django_filters.FilterSet):
    DATETIME_UTC_CHOICES = [
        ('today', _('today')),
        ('3hours', _('last 3 hours')),
        ['1day', _('tomorrow')],
        ['7days', _('7 days')],
    ]

    datetime_utc = DummyChoiceFilter(
        choices=DATETIME_UTC_CHOICES, initial='today')

    def __init__(self, sport, *args, **kwargs):
        super(SessionFilter, self).__init__(*args, **kwargs)
        self.filters['session_round__season__competition'].extra['queryset'] = \
            Competition.objects.filter(sport=sport)
        self.filters['area'].extra['queryset'] = Area.objects.filter(competition__sport=sport).distinct()

    class Meta:
        model = Session
        fields = ['area', 'session_round__season__competition']
