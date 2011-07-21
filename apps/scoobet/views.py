from django.db.models import Q, Avg
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from endless_pagination.decorators import page_template
from django.core import urlresolvers
from django import db

from actstream.models import actor_stream, Follow

from bet.helpers import *
from bet.models import *
from gsm.models import Session, Competition, GsmEntity

@login_required
def status_add(request,
    template_name='scoobet/status_add.html', extra_context=None):
    context = {
        'object': request.user,
    }
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def autocomplete(request,
    template_name='scoobet/autocomplete.html', extra_context=None):
    q = request.GET['q'] # crash if q is not in the url
    context = {
        'q': q,
    }

    queries = {}
    queries['sessions'] = Session.objects.filter(
        Q(oponnent_A_name=q)|Q(oponnent_B_name__istartswith=q)).filter(
        datetime_utc__gte=datetime.date.today()).order_by('datetime_utc').distinct()[:3]
    queries['users'] = User.objects.filter(username__icontains=q)[:3]
    queries['teams'] = GsmEntity.objects.filter(
        ascii_name__icontains=q, tag='team')[:3]
    queries['players'] = GsmEntity.objects.filter(
        ascii_name__icontains=q, tag='person')[:3]
    queries['competitions'] = Competition.objects.filter(
        ascii_name__icontains=q)[:3]
    context.update(queries)

    results = 0
    for query in queries.values():
        results += len(query)
    context['results'] = results

    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def me(request):
    return shortcuts.redirect(urlresolvers.reverse(
        'user_detail', args=(request.user.username,)))

@login_required
def feed_friends(request,
    template_name='scoobet/feed_friends.html', extra_context=None):
    user = request.user

    activities = Action.objects.filter(
        Q(
            action_object_content_type = ContentType.objects.get_for_model(User),
            action_object_object_id = user.pk
        ) | 
        Q(
            actor_content_type = ContentType.objects.get_for_model(User),
            actor_object_id = user.pk
        ) | 
        Q(
            target_content_type = ContentType.objects.get_for_model(User),
            target_object_id = user.pk
        ) |
        Q(
            action_object_content_type = ContentType.objects.get_for_model(User),
            action_object_object_id__in = user.follows()
        ) | 
        Q(
            actor_content_type = ContentType.objects.get_for_model(User),
            actor_object_id__in = user.follows()
        ) | 
        Q(
            target_content_type = ContentType.objects.get_for_model(User),
            target_object_id__in = user.follows()
        )
    ).order_by('-timestamp').distinct()

    context = {
        'activity_list': activities,
        'page_template': 'auth/user_activities_page.html',
    }

    if 'page' in request.GET: 
        template_name = context['page_template']

    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def user_detail(request, username, tab='activities',
    template_name='auth/user_%s.html', extra_context=None):

    context = {}

    user = context['object'] = shortcuts.get_object_or_404(User, 
                                                        username=username)
    if request.user == user:
        context['is_me'] = True
    
    if tab == 'activities':
        context['activity_list'] = Action.objects.filter(
            Q(
                action_object_content_type = ContentType.objects.get_for_model(User),
                action_object_object_id = user.pk
            ) | 
            Q(
                actor_content_type = ContentType.objects.get_for_model(User),
                actor_object_id = user.pk
            ) | 
            Q(
                target_content_type = ContentType.objects.get_for_model(User),
                target_object_id = user.pk
            )
        ).order_by('-timestamp').distinct()
        context['page_template'] = 'auth/user_activities_page.html'
    elif tab == 'social':
        context['follower_list'] = user.follows()
        context['following_list'] = user.following()
        if context['follower_list'].count() > context['following_list'].count():
            context['paginate_list'] = context['follower_list']
        else:
            context['paginate_list'] = context['following_list']
        context['page_template'] = 'auth/user_social_page.html'
    elif tab == 'picks':
        context['bet_list_helper'] = BetListHelper(request, ticket__user=user,
            exclude_filters=['bettype', 'sport', 'competition', 'has_text', 'has_upload'])
    elif tab == 'stats':
        if user.ticket_set.count():
            context['bet_list_helper'] = BetListHelper(request, exclude_filters=[
                'bettype', 'sport', 'competition', 'has_text', 'has_upload'], 
                ticket__user=user)
            context['bet_list_helper'].set_ticket_qs(context['bet_list_helper'].ticket_qs.exclude(bet__correction=BET_CORRECTION_NEW))
            tickets = context['bet_list_helper'].ticket_qs

            total_odds = 0
            balance = 0
            balance_history = context['balance_history'] = []
            context['won_ticket_count'] = 0
            context['lost_ticket_count'] = 0
            context['total_stake'] = 0
            context['total_earnings'] = 0

            for ticket in tickets:
                balance += ticket.profit
                balance_history.append({
                    'ticket': ticket,
                    'balance': balance,
                })

                total_odds += ticket.odds
                context['total_stake'] += ticket.stake
                
                if ticket.correction == BET_CORRECTION_WON:
                    context['total_earnings'] += ticket.stake * ticket.odds
                    context['won_ticket_count'] += 1
                elif ticket.correction == BET_CORRECTION_LOST:
                    context['lost_ticket_count'] += 1

            context['average_odds'] = '%.2f' % (float(total_odds) / len(tickets))
            context['won_ticket_percent'] = int(
                (float(context['won_ticket_count']) / len(tickets)) * 100)
            context['lost_ticket_percent'] = 100 - context['won_ticket_percent']
            context['average_stake'] = '%.2f' % (float(context['total_stake']) / len(tickets))
            context['profit'] = context['total_earnings'] - context['total_stake']
            if context['total_earnings'] > 0:
                context['profitability'] = '%.2f' % ((
                    (context['total_earnings'] - context['total_stake']) / context['total_stake']
                ) * 100)
                int((context['total_stake'] / context['total_earnings'])*100)
            else:
                context['profitability'] = 0
        else:
            context['empty'] = True

    if request.is_ajax() and 'page_template' in context.keys():
        template_name = context['page_template']
    else:
        template_name = template_name % tab

    context.update(extra_context or {})
    ret = shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
    return ret
