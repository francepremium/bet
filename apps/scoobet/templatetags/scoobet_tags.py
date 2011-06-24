from django import template
from django.utils.translation import ugettext as _
from django.db.models import Sum, Q

import scoobet
from bet.models import Ticket, Bet
from gsm.models import AbstractGsmEntity, Sport

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
    ticket_list = None
    blocks = []
    friends = None
    if request.user.is_authenticated():
        friends = request.user.friends()

    """
    Reference block structure

    block_template = {
        'plural_all': '',
        'single_all': '',
        'value_all': None,
        'value_friends': None,
    }
    """

    if obj.__class__.__name__ == 'User':
        block = {
            'plural_all': '%s followers',
            'single_all': '%s follower',
            'plural_friends': 'including %s friends',
            'single_friends': 'including %s friend',
            'value_all': obj.following().count()
        }
        if friends is not None: # avoid executing the friends queryset
            block['value_friends'] = obj.following().filter(pk__in=friends).count()
        blocks.append(block)

        block = {
            'plural_all': '%s follow',
            'single_all': '%s follows',
            'plural_friends': 'including %s friends',
            'single_friends': 'including %s friend',
            'value_all': obj.follows().count()
        }
        if friends is not None: # avoid executing the friends queryset
            block['value_friends'] = obj.follows().filter(pk__in=friends).count()
        blocks.append(block)

    else:
        user_list = obj.fans.all()
        block = {
            'plural_all': '%s bet on it',
            'single_all': '%s bet on it',
            'plural_friends': 'including %s friends',
            'single_friends': 'including %s friend',
            'value_all': user_list.count(),
        }
        if friends is not None: # avoid executing the friends queryset
            block['value_friends'] = user_list.filter(pk__in=friends).count()
        blocks.append(block)

        if obj.__class__.__name__ == 'Bookmaker':
            ticket_list = Ticket.objects.filter(bookmaker=obj)
            block = {
                'plural_all': '%s tickets',
                'single_all': '%s ticket',
                'plural_friends': 'including %s by my friends',
                'single_friends': 'including %s by my friends',
                'value_all': ticket_list.count(),
            }
            if friends is not None:
                block['value_friends'] = ticket_list.filter(user__in=friends).count()
            blocks.append(block)


            stake = lambda x: x.aggregate(Sum('stake'))['stake__sum'] or 0
            block = {
                'plural_all': '%s engaged units',
                'single_all': '%s engaged unit',
                'plural_friends': 'including %s by my friends',
                'single_friends': 'including %s by my friends',
                'value_all': stake(ticket_list),
            }
            if friends is not None:
                block['value_friends'] = stake(
                    ticket_list.filter(user__in=friends))
            blocks.append(block)

        elif isinstance(obj, AbstractGsmEntity) or isinstance(obj, Sport):
            if obj.__class__.__name__ == 'Competition':
                bet_list = Bet.objects.filter(session__season__competition=obj)
            elif obj.__class__.__name__ == 'Session':
                bet_list = Bet.objects.filter(session=obj)
            elif obj.__class__.__name__ == 'Sport':
                bet_list = Bet.objects.filter(session__sport=obj)
            elif getattr(obj, 'tag', False) in ('person', 'team', 'double'):
                bet_list = Bet.objects.filter(
                    Q(session__oponnent_A=obj) |
                    Q(session__oponnent_B=obj)
                )

            block = {
                'plural_all': '%s bets',
                'single_all': '%s bet',
                'plural_friends': 'including %s by my friends',
                'single_friends': 'including %s by my friends',
                'value_all': bet_list.count(),
            }
            if friends is not None:
                block['value_friends'] = bet_list.filter(ticket__user__in=friends).count()
            blocks.append(block)

    # now to make html_all and html_friends
    def html(block, key):
        value = block['value_%s' % key]
        value_html = '<span class="number">%s</span>' % value

        if value > 1:
            tmp = 'plural'
        else:
            tmp = 'single'
        
        block['html_%s' % key] = _(block['%s_%s' % (tmp, key)]) % value_html

    for block in blocks:
        html(block, 'all')
        if friends is not None:
            html(block, 'friends')

    print blocks
    return {
        'request': request,
        'blocks': blocks,
    }
