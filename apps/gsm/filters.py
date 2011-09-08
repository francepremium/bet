import datetime

from django.db import models
from django.utils.translation import ugettext as _

import django_filters as filters

from models import *

CONVERTER = models.DateField()

class DateFilter(filters.Filter):
    def filter(self, qs, value):
        if not value:
            value = datetime.date.today()
        else:
            value = CONVERTER.to_python(value)
            
        next_day = value + datetime.timedelta(days=1)
        qs = qs.filter(
            datetime_utc__gte=value,
            datetime_utc__lte=next_day
        )
        return qs

class SessionFilter(filters.FilterSet):
    filter_overrides =  {
        models.DateTimeField: {
            'filter_class': DateFilter
        },
    }

    class Meta:
        model = Session
        fields = ['datetime_utc']
