from django import forms

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from gsm.models import *
from bookmaker.models import *
from models import *

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        exclude = (
            'user',
        )
    
class PronosticForm(forms.ModelForm):
    sport = forms.ModelChoiceField(Sport.objects.all())
    session = AutoCompleteSelectField('session')

    class Meta:
        model = Pronostic
