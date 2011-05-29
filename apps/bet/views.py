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
                'bet_pronostic_form', args=(bet.pk,)))
    else:
        form = form_class(instance=instance)
   
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def delete(request, bet_pk):
    bet = shortcuts.get_object_or_404(Bet, pk=bet_pk)
    if bet.user != request.user and not request.user.is_staff:
        return http.HttpResponseForbidden()
    if request.POST.get('confirm', False):
        bet.delete()
    return http.HttpResponse(_(u'bet deleted'))

@login_required
def pronostic_delete(request, pronostic_pk):
    pronostic = shortcuts.get_object_or_404(Pronostic, pk=pronostic_pk)
    if pronostic.bet.user != request.user and not request.user.is_staff:
        return http.HttpResponseForbidden()
    bet = pronostic.bet
    if request.POST.get('confirm', False):
        pronostic.delete()
    return shortcuts.redirect(urlresolvers.reverse(
        'bet_pronostic_form', args=(bet.pk,)))

@login_required
def pronostic_form(request, bet_pk, form_class=PronosticForm,
    template_name='bet/pronostic_form.html', extra_context=None):

    context = {}
    context['bet'] = bet = shortcuts.get_object_or_404(Bet, pk=bet_pk)

    if bet.user != request.user and not request.user.is_staff:
        return http.HttpResponseForbidden()

    pronostic_pk = request.GET.get('pronostic', False)
    if pronostic_pk:
        instance = shortcuts.get_object_or_404(Pronostic, pk=pronostic_pk)
        initial = {
            'sport': instance.session.sport,
        }
        context['show_all_fields'] = True
    else:
        instance = Pronostic(bet=bet)
        initial = {}

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            pronostic = form.save()
            return shortcuts.redirect(urlresolvers.reverse(
                'bet_pronostic_form', args=(bet.pk,)))
        else:
            context['show_all_fields'] = True
    else:
        form = form_class(instance=instance, initial=initial)
        if initial.get('sport', False):
            form.fields['bettype'].queryset = BetType.objects.filter(sport=initial['sport'])
            form.fields['choice'].queryset = BetChoice.objects.filter(bettype=instance.bettype)
   
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))


