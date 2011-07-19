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

@login_required
def me(request):
    return shortcuts.redirect(urlresolvers.reverse(
        'user_detail', args=(request.user.username,)))

def user_detail(request, username, tab='activities',
    template_name='auth/user_%s.html', extra_context=None):

    context = {}

    user = context['object'] = shortcuts.get_object_or_404(User, 
                                                        username=username)
    if request.user == user:
        context['is_me'] = True
    
    if tab == 'activities':
        context['activity_list'] = actor_stream(user)
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
    print 'rendering', len(db.connection.queries), 'queries'
    ret = shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
    print 'done rendering', len(db.connection.queries), 'queries'
    return ret
