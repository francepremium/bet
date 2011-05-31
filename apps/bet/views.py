from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic

from models import *
from forms import *

class BetListView(generic.ListView):
    model = Bet
    context_object_name = 'bet_list'

@login_required
def ticket_add(request, form_class=TicketForm,
    template_name='bet/ticket_add.html', extra_context=None):

    context = {}
    instance = Ticket(user=request.user)
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            ticket = form.save()
            return shortcuts.redirect(urlresolvers.reverse(
                'bet_form', args=(ticket.pk,)))
    else:
        form = form_class(instance=instance)
   
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def ticket_delete(request, ticket_pk):
    ticket = shortcuts.get_object_or_404(Ticket, pk=ticket_pk)
    if ticket.user != request.user and not request.user.is_staff:
        return http.HttpResponseForbidden()
    if request.POST.get('confirm', False):
        ticket.delete()
    return http.HttpResponse(_(u'ticket deleted'))

@login_required
def bet_delete(request, bet_pk):
    bet = shortcuts.get_object_or_404(Bet, pk=bet_pk)
    if bet.ticket.user != request.user and not request.user.is_staff:
        return http.HttpResponseForbidden()
    ticket = bet.ticket
    if request.POST.get('confirm', False):
        bet.delete()
    return shortcuts.redirect(urlresolvers.reverse(
        'bet_form', args=(bet.ticket.pk,)))

@login_required
def bet_form(request, ticket_pk, form_class=BetForm,
    template_name='bet/bet_form.html', extra_context=None):

    context = {}
    context['ticket'] = ticket = shortcuts.get_object_or_404(Ticket, pk=ticket_pk)

    if ticket.user != request.user and not request.user.is_staff:
        return http.HttpResponseForbidden()

    bet_pk = request.GET.get('bet', False)
    if bet_pk:
        instance = shortcuts.get_object_or_404(Bet, pk=bet_pk)
        context['show_all_fields'] = True
    else:
        instance = Bet(ticket=ticket)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            bet = form.save()
            return shortcuts.redirect(urlresolvers.reverse(
                'bet_form', args=(ticket.pk,)))
        else:
            context['show_all_fields'] = True
    else:
        form = form_class(instance=instance)
        if instance.pk:
            form.fields['bettype'].queryset = BetType.objects.filter(sport=instance.session.sport)
            form.fields['choice'].queryset = BetChoice.objects.filter(bettype=instance.bettype)
   
    context['form'] = form

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))


