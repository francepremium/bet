import copy

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
    def __init__(self, request, qs=Bet.objects.all(), paginate=True, **kwargs):
        self.request = request
        self.paginate = paginate
        self.exclude = []
        self.exclude_filters = []
        self.exclude_columns = []
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
                self.exclude_columns.append('competition')
            if exclude_key == 'competition':
                self.exclude.append('sport')
            if exclude_key in ('team', 'person', 'double'):
                self.exclude.append('sport')
        self.exclude_filters += self.exclude
        self.exclude_columns += self.exclude
        self.qs = self.qs.filter(**kwargs)

        self.filter = BetFilter(request.GET, queryset=self.qs)
        
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

    def render_ticket_table(self):
        context = template.Context()
        context.update({
            'ticket_list': Ticket.objects.filter(bet__in=self.qs).distinct(),
            'request': request,
            'paginate': self.paginate,
            'exclude_filters': self.exclude_filters,
            'exclude_columns': self.exclude_columns,
        })

        t = template.loader.select_template([
            'bet/_includes/ticket_list_table.html'])
        return t.nodelist.render(context)
