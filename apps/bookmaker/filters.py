import datetime

from django.utils.translation import ugettext as _

import django_filters

from models import *

class BetTypeFilter(django_filters.FilterSet):
    class Meta:
        model = BetType
        fields = ['sport']
