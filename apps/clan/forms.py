from django import forms

from models import *

class ClanForm(forms.ModelForm):
    class Meta:
        model = Clan
        exclude = ('creation_user', 'creation_datetime', 'auto_approve')
