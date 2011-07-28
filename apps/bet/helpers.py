import copy

from django.db.models import Avg, Max, Min, Count
from django.db.models.query import QuerySet
from django.db.models import Q
from django import template

from gsm.models import Sport
from filters import *
from models import *

class BetListHelper(object):
    """
    Useage:

    # in sport detail view
    context['bet_list_helper'] = BetListHelper(
        request, 
        qs=Bet.objects.filter(session__sport=sport.pk),
        exclude = ['sport']
    )
    
    # in sport detail template template
    {{ bet_list_helper.render_form }}
    {{ bet_list_helper.render_list }}
    """
    def __init__(self, request, qs=None, paginate=True, 
                exclude_filters=None, exclude_columns=None, exclude=None, **kwargs):
        self.request = request
        self.paginate = paginate
        self.exclude = exclude or []
        self.exclude_filters = exclude_filters or []
        self.exclude_columns = exclude_columns or []
        if qs is None:
            self.qs = Bet.objects.all()
        else:
            self.qs = qs
        self.sport = None

        # handling "magic" kwargs, to clean kwargs before 
        # it is passed to qs.filter
        for key, value in kwargs.items():
            if hasattr(value, 'sport'):
                self.sport = value.sport
            if isinstance(value, Sport):
                self.sport = value

            if key in ('team', 'person', 'double'):
                self.qs = self.qs.filter(
                    models.Q(session__oponnent_A=value) |
                    models.Q(session__oponnent_B=value)
                )
                kwargs.pop(key)

            # for session__season__competition, it would be: competition
            exclude_key = key.split('__')[-1]

            self.exclude.append(exclude_key)
            if exclude_key == 'session':
                self.exclude.append('sport')
            if exclude_key == 'competition':
                self.exclude.append('sport')
            if exclude_key in ('team', 'person', 'double'):
                self.exclude.append('sport')
        self.exclude_filters += self.exclude
        self.exclude_columns += self.exclude

        if kwargs:
            self.qs = self.qs.filter(**kwargs)

        if isinstance(self.qs, QuerySet):
            self.filter = BetFilter(request.GET, queryset=self.qs)
            self.qs = self.filter.qs
            self.qs = self.qs.annotate(Count('ticket__bet'))
            self.qs = self.qs.select_related('session__season__competition', 'bettype', 'choice', 'ticket__user', 'ticket__bokmaker')
        else:
            self.filter = None

        if self.filter:
            # clean filter
            excludes = self.exclude_filters + kwargs.keys()
            for key in self.filter.form.fields.keys():
                exclude_key = key.split('__')[-1]
                if exclude_key in excludes or key in excludes:
                    self.filter.form.fields.pop(key)
                    self.filter.filters.pop(key)

            if self.sport:
                if 'session__season__competition' in self.filter.form.fields:
                    self.filter.form.fields['session__season__competition'].queryset = \
                        self.filter.form.fields['session__season__competition'].queryset.filter(
                            sport=self.sport)
                if 'ticket__bookmaker' in self.filter.form.fields:
                    self.filter.form.fields['ticket__bookmaker'].queryset = \
                        self.filter.form.fields['ticket__bookmaker'].queryset.filter(
                            bettype__sport=self.sport).distinct()
                if 'bettype' in self.filter.form.fields:
                    self.filter.form.fields['bettype'].queryset = \
                        self.filter.form.fields['bettype'].queryset.filter(
                            sport=self.sport)

        user = self.request.user
        if user.is_authenticated():
            for bet in self.qs:
                if user.betprofile.can_correct(bet):
                    bet.can_correct = True
                if user.betprofile.can_flag(bet):
                    bet.can_flag = True

    def render_form(self):
        context = template.Context()
        context.update({
            'filter': self.filter,
            'request': self.request,
            'sport': self.sport,
        })

        t = template.loader.select_template([
            'bet/_includes/bet_list_form.html'])
        return t.nodelist.render(context)

    def render_bet_table(self):
        context = template.Context()
        context.update({
            'bet_list': self.qs,
            'request': self.request,
            'paginate': self.paginate,
            'exclude_filters': self.exclude_filters,
            'exclude_columns': self.exclude_columns,
        })
 
        t = template.loader.select_template([
            'bet/_includes/bet_list_table.html'])
        return t.nodelist.render(context)
 
    def set_ticket_qs(self, ticket_qs):
        self._ticket_qs = ticket_qs

    @property
    def ticket_qs(self):
        if not hasattr(self, '_ticket_qs'):
            self._ticket_qs = Ticket.objects.filter(bet__in=self.qs).distinct()
        return self._ticket_qs
 
    def render_ticket_table(self):
        context = template.Context()
        context.update({
            'ticket_list': self.ticket_qs,
            'request': self.request,
            'paginate': self.paginate,
            'exclude_filters': self.exclude_filters,
            'exclude_columns': self.exclude_columns,
        })
 
        t = template.loader.select_template([
            'bet/_includes/ticket_list_table.html'])
        return t.nodelist.render(context)
