from django import template
from django.db import models

from bet.models import Bet
from bet.filters import BetFilter

register = template.Library()

@register.tag(name='render_bet_list')
def render_bet_list(parser, token):
    """
    Arguments:
    - sport=x: context['x'] is a sport instance or pk
    - team=x: context['x'] is a team instance or pk
    - session=x: context['x'] is a session instance or pk
    - user=x: context['x'] is a user instance or pk
    - bookmaker=x: context['x'] is a bookmaker instance or pk
    """
    kwargs = {}
    for arg in token.split_contents()[1:]:
        equal = arg.find('=')
        if equal:
            kwargs[arg[:equal]] = arg[equal+1:]
        else:
            kwargs[arg] = True
    
    return BetListNode(**kwargs)

class BetListNode(template.Node):
    def __init__(self, **kwargs):
        """ OMG UGLY VOODOO """
        self.kwargs = {}

        for k, v in kwargs.items():
            try:
                is_int = str(int(v)) == v
            except:
                is_int = False
            
            if v[0] == '"' or v[0] == "'":
                self.kwargs[k] = v[1:-1]
            elif is_int:
                self.kwargs[k] = v
            else:
                self.kwargs[k] = template.Variable(v)

    def render(self, context):
        for k, v in self.kwargs.items():
            if hasattr(v, 'resolve'):
                self.kwargs[k] = v.resolve(context)
                if isinstance(self.kwargs[k], models.Model):
                    self.kwargs[k] = str(self.kwargs[k].pk)

        qs = self.kwargs.pop('qs', False)
        if not qs:
            qs = Bet.objects.all()

        team = self.kwargs.pop('team', False)
        if team:
            qs = qs.filter(
                models.Q(session__oponnent_A=team) |
                models.Q(session__oponnent_B=team)
            )

        bookmaker = self.kwargs.pop('bookmaker', False)
        if bookmaker:
            qs = qs.filter(ticket__bookmaker=bookmaker)

        user = self.kwargs.pop('user', False)
        if user:
            qs = qs.filter(ticket__user=user)

        session = self.kwargs.pop('session', False)
        if session:
            qs = qs.filter(session=session)
        
        qd = {}
        sport = context.get('sport', False)
        if sport:
            qd['session__sport'] = context['sport'].pk
        for k,v in context['request'].GET.items():
            qd[k] = v
        qd.update(self.kwargs)
        context['filter'] = f = BetFilter(qd, queryset=qs)

        context['bet_list'] = f.qs

        if not hasattr(self, 'nodelist'):
            t = template.loader.select_template([
                'bet/_includes/bet_list.html',
            ])
            self.nodelist = t.nodelist
        
        return self.nodelist.render(context)
