from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic

import actstream
from subscription.examples.yourlabs.shortcuts import emit_static

from bet.helpers import *
from models import *
from forms import *
from filters import *

class BetDetailView(generic.DetailView):
    model = Bet
    context_object_name = 'bet'

class TicketDetailView(generic.DetailView):
    model = Ticket
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super(TicketDetailView, self).get_context_data(**kwargs)
        exclude_columns = ['stake', 'user']
        context['bet_list_helper'] = BetListHelper(self.request, context['ticket'].bet_set.all(), exclude_columns=exclude_columns)
        return context

class BetListView(generic.ListView):
    model = Bet
    context_object_name = 'bet_list'
    to_correct = False
    flagged = False
    preset = {}

    def get_queryset(self):
        qs = super(BetListView, self).get_queryset()
        
        if self.kwargs.get('tab', False) == 'mine':
            qs = qs.filter(ticket__user=self.request.user)
        elif self.kwargs.get('tab', False) == 'friends':
            qs = qs.filter(ticket__user__in=self.request.user.friends())
        
        if self.to_correct:
            qs = qs.filter(correction=BET_CORRECTION_NEW)
        elif self.flagged:
            qs = qs.filter(flagged=True)

        return qs

    def get_context_data(self, **kwargs):
        context = super(BetListView, self).get_context_data(**kwargs)
        context['bet_list_helper'] = BetListHelper(self.request, context['bet_list'], exclude_filters=['user'], exclude_columns=['support', 'time', 'sport', 'competition'])

        if self.to_correct:
            urlname = 'bet_list_to_correct_tab'
        elif self.flagged:
            urlname = 'bet_list_flagged_tab'
        else:
            urlname = 'bet_list_tab'
        
        for tab in ('mine', 'friends', 'all'):
            context['%s_url' % tab] = urlresolvers.reverse(urlname, args=(tab,))

        return context

@login_required
def ticket_add(request, form_class=TicketForm,
    template_name='bet/ticket_add.html', extra_context=None):

    # if there is any pending ticket, force it
    tickets = request.user.ticket_set.filter(status=TICKET_STATUS_INCOMPLETE).order_by('-pk')
    if tickets:
        return shortcuts.redirect(urlresolvers.reverse(
            'bet_form', args=(tickets[0].pk,)) + '?forced=1')

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
    if request.POST.get('noredirect', False):
        if ticket.pk:
            message = _('bet deleted')
        else:
            message = _('bet deleted, ticket without bet deleted too')
        messages.success(request, message)
        return shortcuts.redirect(request.META.get('HTTP_REFERER', '/'))

    if ticket.pk:
        return shortcuts.redirect(urlresolvers.reverse(
            'bet_form', args=(ticket.pk,)))
    else:
        return http.HttpResponse(_('ticket without bets deleted'))

@login_required
def bet_flag(request):
    bet = shortcuts.get_object_or_404(Bet, pk=request.GET.get('bet_pk'))
    bet.flagged = True
    bet.save()
    return http.HttpResponse('OK', status=201)

@login_required
def bet_form(request, ticket_pk, form_class=BetForm,
    template_name='bet/bet_form.html', extra_context=None):

    context = {}
    context['ticket'] = ticket = shortcuts.get_object_or_404(Ticket, pk=ticket_pk)
    action = request.POST.get('action', 'save_and_add_another')
    
    if ticket.user != request.user and not request.user.is_staff:
        return http.HttpResponseForbidden()

    bet_pk = request.GET.get('bet', False)
    if bet_pk:
        instance = shortcuts.get_object_or_404(Bet, pk=bet_pk)
        context['show_all_fields'] = True
    else:
        instance = Bet(ticket=ticket)

    if request.method == 'POST':
        if action == 'just_close':
            ticket.status = TICKET_STATUS_DONE
            ticket.save()
            return http.HttpResponse(_('ticket closed'), status=201)
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            bet = form.save()
            if action == 'save_and_close':
                ticket.status = TICKET_STATUS_DONE
                ticket.save()
                actstream.action.send(request.user, verb='closed ticket', action_object=ticket)
                return http.HttpResponse(
                    _('bet saved and ticket closed'), status=201)
            elif action == 'save_and_add_another':
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


