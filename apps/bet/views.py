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

@login_required
def add(request, form_class=BetForm,
    template_name='bet/add.html', extra_context=None):

    context = {}
    instance = Bet(user=request.user)
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            bet = form.save()
            return shortcuts.redirect(urlresolvers.reverse(
                'bet_add_pronostic', args=(bet.pk,)))
    else:
        form = form_class(instance=instance)
   
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def add_pronostic(request, bet_pk, form_class=PronosticForm,
    template_name='bet/add_pronostic.html', extra_context=None):

    context = {}
    context['bet'] = bet = shortcuts.get_object_or_404(Bet, pk=bet_pk)
    instance = Pronostic(bet=bet)
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            pronostic = form.save()
            return shortcuts.redirect(urlresolvers.reverse(
                'bet_add_pronostic', args=(bet.pk,)))
    else:
        form = form_class(instance=instance)
   
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))


