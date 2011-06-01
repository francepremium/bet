from django import forms
from django.utils.translation import ugettext as _

import django_filters as filters

from models import *

class ClanFilter(filters.FilterSet):
    class Meta:
        model = Clan
        fields = ['name']
