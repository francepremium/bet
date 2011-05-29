from django import forms
from django.utils.translation import ugettext as _

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
    #competition = forms.ModelChoiceField(Competition.objects.all())
    #session = forms.ModelChoiceField(Session.objects.all())
    session = AutoCompleteSelectField('session')

    def clean_session(self):
        session = self.cleaned_data['session']

        for p in self.instance.bet.pronostic_set.all():
            if self.instance.pk and p.pk == self.instance.pk:
                continue
            if p.session.pk == session.pk:
                raise forms.ValidationError(_(u'there is already a pronostic for this match in this combined bet. Please choose another match'))
        
        return session

    class Meta:
        model = Pronostic
        exclude = (
            'bet',
        )
