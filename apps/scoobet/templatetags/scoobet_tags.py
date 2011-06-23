from django import template
from django.db.models import Sum

import scoobet
from bet.models import Ticket, Bet

register = template.Library()

@register.filter
def group_activities(activities):
    return scoobet.group_activities(activities)

@register.inclusion_tag('auth/_includes/user_list.html')
def render_user_list(request, user_list):
    return {
        'request': request,
        'user_list': user_list,
    }

@register.inclusion_tag('scoobet/_includes/popularity.html')
def render_popularity_for_object(request, obj):
    if obj.__class__.__name__ == 'Bookmaker':
        tickets = Ticket.objects.filter(bookmaker=obj)
        users = obj.fans.all()

    popularity = {
        'user_count': users.count(),
        'stake_sum': tickets.aggregate(Sum('stake'))['stake__sum'],
        'ticket_count': tickets.count(),
    }

    if request.user.is_authenticated():
        popularity['friend_user_count'] = users.filter(pk__in=request.user.friends().values_list('pk')).count()
        popularity['friend_stake_sum'] = tickets.filter(user__in=request.user.friends()).aggregate(Sum('stake'))['stake__sum'] or 0
        popularity['friend_ticket_count'] = tickets.filter(user__in=request.user.friends()).count()

    return {
        'popularity': popularity,
    }
