from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from models import *
from forms import *

def add(request,
    template_name='bet/add.html', extra_context=None):
    if not request.user.is_authenticated():
        return http.HttpResponseForbidden()

    context = {}
    form_class = BetForm
    instance = Bet(user=request.user)
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            bet = form.save()
            messages.success(request, _(u'bet saved'))
    else:
        form = form_class(instance=instance)
   
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
