from django import forms
from django.utils.translation import ugettext as _

from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

from gsm.models import *
from bookmaker.models import *
from models import *

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = (
            'user',
            'status',
        )
    
class BetForm(forms.ModelForm):
    #competition = forms.ModelChoiceField(Competition.objects.all())
    #session = forms.ModelChoiceField(Session.objects.all())
    session = AutoCompleteSelectField('session')

    def clean_session(self):
        session = self.cleaned_data['session']

        for bet in self.instance.ticket.bet_set.all():
            if self.instance.pk and bet.pk == self.instance.pk:
                continue
            if bet.session.pk == session.pk:
                raise forms.ValidationError(_(u'there is already a pronostic for this match in this combined bet. Please choose another match'))
        
        return session

    def __init__(self, *args, **kwargs):
        super(BetForm, self).__init__(*args, **kwargs)

        session_pk = self.data.get('session', None)
        if session_pk:
            session = Session.objects.get(pk=session_pk)
            self.fields['bettype'].queryset = BetType.objects.filter(
                                                sport=session.sport)

        bettype_pk = self.data.get('bettype', None)
        if bettype_pk:
            self.fields['choice'].queryset = BetChoice.objects.filter(
                                                bettype__pk=bettype_pk)

    class Meta:
        model = Bet
        exclude = (
            'ticket',
            'status',
            'correction',
        )
