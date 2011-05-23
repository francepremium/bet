from django import forms
from django.forms.models import BaseModelFormSet

from models import *

class BookmakerForm(forms.ModelForm):
    class Meta:
        model = Bookmaker
        exclude = (
            'user',
            'bettype',
        )

class BetTypeForm(forms.ModelForm):
    class Meta:
        model = BetType
        fields = (
            'sport',
            'name_fr',
            'name_en',
        )

    def validate_unique(self):
        """
        Calls the instance's validate_unique() method and updates the form's
        validation errors if any were raised.
        """
        exclude = self._get_validation_exclusions()
        exclude.remove("name") # remove our previously excluded field from the list.

        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError, e:
            self._update_errors(e.message_dict)

class BetChoiceForm(forms.ModelForm):
    class Meta:
        model = BetChoice
