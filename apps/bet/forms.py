from django import forms

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from gsm.models import *
from bookmaker.models import *
from models import *

class BetForm(forms.ModelForm):
    sport = forms.ModelChoiceField(Sport.objects.all())
    session = AutoCompleteSelectField('session')
    bettype = forms.ModelChoiceField(BetType.objects.none())
    choice = forms.ModelChoiceField(BetChoice.objects.none())

    class Meta:
        model = Bet
        exclude = (
            'user',
        )
