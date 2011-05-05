import datetime

from django.db.models import Q
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.utils.translation import get_language_from_request

from models import *
from filters import *

import gsm

def get_language_from_request(request):
    return 'en'

def team_detail(request, sport, gsm_id, tag='team'):
    sport = shortcuts.get_object_or_404(Sport, slug=sport)
    gsm_entity_class = model_class_for_tag(tag)
    team, created = gsm_entity_class.objects.get_or_create(
        sport=sport, tag=tag, gsm_id=gsm_id)
    return shortcuts.redirect(team.get_home_absolute_url())

def team_detail_tab(request, sport, gsm_id, tab, tag='team',
    update=False,
    template_name='', extra_context=None):
    sport = shortcuts.get_object_or_404(Sport, slug=sport)
    gsm_entity_class = model_class_for_tag(tag)
    team, created = gsm_entity_class.objects.get_or_create(
        sport=sport, tag=tag, gsm_id=gsm_id)

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
        'team': team,
    }

    template_name = [
        'gsm/%s/%s/%s.html' % (sport.slug, tag, tab),
        'gsm/%s/%s.html' % (tag, tab),
    ]

    def get_reference_season(team):
        # find reference seasons for stats
        q = Competition.objects.filter(sport=sport)
        q = q.filter(is_nationnal=True)
        q = q.filter(
            Q(season__round__session__in=team.sessions_as_A.all()) |
            Q(season__round__session__in=team.sessions_as_B.all())
        ).distinct()
        reference_competition = q[q.count() - 1]
        q = reference_competition.season_set.all().order_by('-gsm_id')
        reference_season = q[q.count() - 1]
        return reference_season

    def get_rankings_for_season(season):
        # get stats
        tree = gsm.get_tree(context['language'], sport,
            'get_tables', id=season.gsm_id, type='season')
        group_elements = tree.findall('competition/season/round/group')
        resultstable_elements = tree.findall('competition/season/round/resultstable')
        if group_elements and not resultstable_elements:
            for group_element in group_elements:
                print group_element
        for resultstable in resultstable_elements:
            if resultstable.attrib['type'] == 'total':
                break

        return resultstable.findall('ranking')

    if tab == 'home':
        # find next sessions
        q = Session.objects.filter(sport=sport)
        q = q.filter(Q(oponnent_A=team)|Q(oponnent_B=team))
        context['next_sessions'] = q[:7]

        reference_season = get_reference_season(team)
        context['rankings'] = get_rankings_for_season(reference_season)

    elif tab == 'squad':
        # season filter
        context['team_seasons'] = Season.objects.filter(
            Q(round__session__in=team.sessions_as_A.all()) |
            Q(round__session__in=team.sessions_as_B.all())
        ).distinct().order_by('datetime_utc')
        if 'season_gsm_id' in request.GET and request.GET['season_gsm_id']:
            season = shortcuts.get_object_or_404(Season, gsm_id=request.GET['season_gsm_id'])
        else:
            season = context['team_seasons'][0]
        context['season'] = season

        # squad finder
        tree = gsm.get_tree(context['language'], sport,
            'get_squads', type='season', id=season.gsm_id, detailed='yes',
            statistics='yes')
        for team_element in tree.findall('team'):
            if str(team.gsm_id) == team_element.attrib['team_id']:
                break

        context['persons'] = []

        # we need to cut this data as well to get minutes played,
        # lineups and subs on bench
        #career_tree = gsm.get_tree(context['language'], sport,
            #'get_career', type='team', detailed='yes', 
            #id=team.gsm_id)

        # person orderer
        positions = {}
        for person_element in team_element.findall('person'):
            if person_element.attrib['type'] == 'player':
                position = person_element.attrib['position']
            else:
                continue # pass coach and crap
                #position = person_element.attrib['type']
            if position not in positions.keys():
                positions[position] = []
            person = GsmEntity(tag='person', sport=sport,
                gsm_id=person_element.attrib['person_id'],
                name=person_element.attrib['name'])

            person.element = person_element
            positions[position].append(person)
            context['persons'].append(person)
        context['positions'] = positions
    elif tab == 'statistics':
        reference_season = get_reference_season(team)
        context['rankings'] = get_rankings_for_season(reference_season)

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def entity_list(request, sport, tag, 
    update=False,
    template_name='', extra_context=None):

    sport = shortcuts.get_object_or_404(Sport, slug=sport)

    template_name = (
        template_name,
        'gsm/%s/%s_list.html' % (sport, tag),
        'gsm/%s_list.html' % tag,
    )

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
    }

    context['tree'] = gsm.get_tree(
        context['language'], 
        sport,
        'get_%ss' % tag,
        update=update
    )

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def entity_detail(request, sport, tag, gsm_id,
    update=True,
    template_name='', extra_context=None):

    sport = shortcuts.get_object_or_404(Sport, slug=sport)

    template_name = (
        template_name,
        'gsm/%s/%s_detail.html' % (sport, tag),
        'gsm/%s_detail.html' % tag,
    )

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
    }

    gsm_entity_class = model_class_for_tag(tag)
    
    entity, created = gsm_entity_class.objects.get_or_create(
        sport = sport,
        tag = tag,
        gsm_id = gsm_id
    )
    context['entity'] = entity

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def sport_detail(request, sport,
    template_name='', extra_context=None):
    sport = shortcuts.get_object_or_404(Sport, slug=sport)
    return shortcuts.redirect(sport.get_matches_absolute_url())

def sport_detail_tab(request, sport, tab,
    template_name='', extra_context=None):
    sport = shortcuts.get_object_or_404(Sport, slug=sport)

    template_name = (
        template_name,
        'gsm/%s/%s.html' % (sport.slug, tab),
        'gsm/sport/%s.html' % tab,
    )

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
    }

    sessions_qs = Session.objects.all()
    sessions_qs = sessions_qs.filter(sport=sport)

    datefilter = request.GET.get('datetime_utc', 'today')
    today = datetime.date.today()
    now = datetime.datetime.now()
    yesterday = datetime.date.today() - datetime.timedelta(1)
    tomorrow = datetime.date.today() + datetime.timedelta(1)
    week = datetime.timedelta(7)

    if tab == 'results':
        sessions_qs = sessions_qs.filter(datetime_utc__lte=tomorrow)
        sessions_qs = sessions_qs.exclude(status='Fixture')
        if datefilter == '3hours':
            sessions_qs = sessions_qs.filter(datetime_utc__gte=now - datetime.timedelta(0, 0, 0, 0, 0, 3))
        elif datefilter == 'today':
            sessions_qs = sessions_qs.filter(datetime_utc__gte=today)
        elif datefilter == '1day':
            sessions_qs = sessions_qs.filter(datetime_utc__gte=yesterday)
        elif datefilter == '7days':
            sessions_qs = sessions_qs.filter(datetime_utc__gte=today - week)
        order = '-datetime_utc'
    elif tab == 'matches':
        sessions_qs = sessions_qs.filter(status='Fixture')
        if datefilter == '3hours':
            sessions_qs = sessions_qs.filter(datetime_utc__gte=now - datetime.timedelta(0, 0, 0, 0, 0, 3))
        elif datefilter == 'today':
            sessions_qs = sessions_qs.filter(datetime_utc__gte=today)
            sessions_qs = sessions_qs.filter(datetime_utc__lte=tomorrow)
        elif datefilter == '1day':
            sessions_qs = sessions_qs.filter(datetime_utc__lte=tomorrow)
        elif datefilter == '7days':
            sessions_qs = sessions_qs.filter(datetime_utc__lte=today + week)
        order = 'datetime_utc'

    if tab in ('matches', 'results'):
        sessions_qs = sessions_qs.order_by(order)
        f = SessionFilter(sport, request.GET, sessions_qs)
        context['filter'] = f

    if tab == 'results':
        f.filters['datetime_utc'].extra['choices'][2][1] = _('yesterday')
        f.filters['datetime_utc'].extra['choices'][3][1] = _('last 7 days')
    elif tab == 'matches':
        f.filters['datetime_utc'].extra['choices'][2][1] = _('tomorrow')
        f.filters['datetime_utc'].extra['choices'][3][1] = _('next 7 days')

    if tab == 'home':
        sessions_qs = Session.objects.filter(sport=sport, status='Fixture').order_by('datetime_utc')

    context['next_sessions'] = sessions_qs[:7]

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
