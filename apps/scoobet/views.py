import datetime

from django.utils import simplejson
from django.db.models import Q, Avg, Count
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

from emailconfirmation.models import EmailConfirmation
from actstream.models import actor_stream, Follow, Action
from avatar.views import add

from bookmaker.models import *
from bet.helpers import *
from bet.models import *
from gsm.models import Session, Competition, GsmEntity
import search_sites

def action_detail(request, action_id):
    """
    ``Action`` detail view (pretty boring, mainly used for get_absolute_url)
    """
    action = shortcuts.get_object_or_404(Action, pk=action_id)
    try:
        new_action = action.action_object.content_object
        if new_action.__class__.__name__ == 'Action':
            action = new_action
    except:
        pass
    return shortcuts.render_to_response('activity/detail.html', {
        'action': action,
    }, context_instance=template.RequestContext(request))

def homepage(request,
    template_name='homepage.html', extra_context=None):
    if request.user.is_authenticated():
        return shortcuts.redirect(urlresolvers.reverse('scoobet_feed_friends'))
    return shortcuts.render(request, template_name, extra_context)

def leaderboard(request, tab='month',
    template_name='leaderboard.html', extra_context=None):

    qs = User.objects.exclude(betprofile__profit=None).annotate(
        cnt=Count('ticket')).filter(cnt__gt=7).select_related('betprofile')

    if tab == 'all':
        profitability_order = '-betprofile__profitability'
        profit_order = '-betprofile__profit'
    elif tab == 'week':
        qs = qs.exclude(betprofile__week_tickets=0)
        profitability_order = '-betprofile__week_profitability'
        profit_order = '-betprofile__week_profit'
    elif tab == 'month':
        qs = qs.exclude(betprofile__month_tickets=0)
        profitability_order = '-betprofile__month_profitability'
        profit_order = '-betprofile__month_profit'

    context = {
        'tab': tab,
        'users_by_profitability': qs.order_by(profitability_order)[:50],
        'users_by_profit': qs.order_by(profit_order)[:50],
        'user_count': User.objects.all().count(),
    }
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def status_add(request,
    template_name='scoobet/status_add.html', extra_context=None):
    context = {
        'object': request.user,
    }
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

@login_required
def following_autocomplete(request):
    term = request.GET['term']

    q = request.user.following().filter(
        Q(username__icontains=term)
    )
    result = []
    for user in q:
        result.append({
            'id': user.username,
            'value': user.username,
            'label': user.username,
        })
    return http.HttpResponse(simplejson.dumps(result))

def autocomplete(request,
    template_name='scoobet/autocomplete.html', extra_context=None):

    if 'q' not in request.GET.keys():
        return http.HttpResponseBadRequest()

    q = request.GET['q']
    context = {
        'q': q,
    }

    queries = {}
    queries['sessions'] = Session.objects.filter(
        start_datetime__gte=datetime.date.today()).filter(
        Q(name_ascii_fr__icontains=q)|Q(name_fr__icontains=q)|
        Q(name_ascii_en__icontains=q)|Q(name_en__icontains=q)).order_by(
            'start_datetime').distinct()[:3]
    queries['users'] = User.objects.filter(username__icontains=q, 
        bookmaker=None)[:3]
    queries['teams'] = GsmEntity.objects.filter(
        Q(name_ascii_fr__icontains=q)|Q(name_fr__icontains=q)|
        Q(name_ascii_en__icontains=q)|Q(name_en__icontains=q), tag='team')[:3]
    queries['players'] = GsmEntity.objects.filter(
        Q(name_ascii_en__icontains=q)|Q(name_en__icontains=q)|
        Q(name_ascii_fr__icontains=q)|Q(name_fr__icontains=q), tag='person')[:3]
    queries['competitions'] = Competition.objects.filter(
        Q(name_ascii_fr__icontains=q)|Q(name_fr__icontains=q)|
        Q(name_ascii_en__icontains=q)|Q(name_en__icontains=q))[:3]
    queries['bookmakers'] = Bookmaker.objects.filter(
        name__icontains=q)[:3]
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
        'object': user,
        'activity_list': activities,
        'page_template': 'auth/user_activities_page.html',
    }

    if 'page' in request.GET: 
        template_name = context['page_template']

    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def user_detail(request, username, tab='activities',
    template_name='auth/user_%s.html', extra_context=None):

    context = {
        'tab': tab,
    }

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
    elif tab == 'picks':
        context['bet_list_helper'] = BetListHelper(request, ticket__user=user,
            exclude_filters=['bettype', 'sport', 'competition', 'has_text', 'has_upload'])
    elif tab == 'stats':
        context['bet_list_helper'] = BetListHelper(request, exclude_filters=[
            'bettype', 'sport', 'competition', 'has_text', 'has_upload'], 
            ticket__user=user)
        context['bet_list_helper'].set_ticket_qs(context['bet_list_helper'].ticket_qs.exclude(bet__correction=BET_CORRECTION_NEW).order_by('pk'))

        tickets = context['bet_list_helper'].ticket_qs
        if len(tickets):
            context.update(user.betprofile.calculate(tickets))
        else:
            context['empty'] = True
    elif tab == 'file':
        context['teams'] = user.gsmentity_set.filter(tag='team')
        context['persons'] = user.gsmentity_set.filter(tag='person')

    if request.is_ajax() and 'page_template' in context.keys():
        template_name = context['page_template']
    else:
        template_name = template_name % tab

    context.update(extra_context or {})
    ret = shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
    return ret


def avatar_upload(request):
    if request.method != 'POST':
        return
    if not request.FILES:
        return

    return add(request, next_override=request.META['HTTP_REFERER'])
