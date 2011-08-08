import datetime

from django import http
from django import shortcuts
from django import template
from django.db.models import get_model
from django.db.models import Q
from django.template import defaultfilters
from django.contrib.auth import decorators
from django.conf import settings
from django.utils import simplejson
from django.contrib import messages
from django.forms.models import modelform_factory

from models import *
from forms import *

def homepage(request, form_class=LeadForm,
    template_name='beta_homepage.html', extra_context=None):

    lead = False
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            lead = form.save()
    else:
        form = form_class()

    context = {
        'form': form,
        'lead': lead,
    }
    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
