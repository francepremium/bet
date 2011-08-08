# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from models import *

class LeadForm(forms.ModelForm):
    def clean_email(self, ):
        data = self.cleaned_data['email']
        if Lead.objects.filter(email=data):
            raise forms.ValidationError(u'%s est déjà inscrit' % data)
        else:
            return data
    class Meta:
        model = Lead
        fields = ['email']
