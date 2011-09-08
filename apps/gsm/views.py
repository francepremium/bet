from collections import OrderedDict
import datetime
from dateutil.rrule import rrule, WEEKLY

from django.db.models import Q
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django import template
from django import http
from django import shortcuts
from django.conf import settings
from django.contrib import messages
from django.utils.translation import get_language_from_request
from django.contrib.auth.decorators import login_required
from django.db import models

import actstream
from actstream.models import actor_stream, Follow, Action

from bet.helpers import *
import gsm

from models import *
from filters import *

#def get_language_from_request(request):
    #return 'fr'

def get_sport_or_404(slug):
    try:
        return Sport.objects.get_for_slug(slug)
    except Sport.DoesNotExist:
        raise http.Http404(_('Could not find sport %s') % slug)

def timezone_adjust(request):
    if not request.POST.get('timezone_offset', False):
        return http.HttpResponseBadRequest('need POST timezone_offset')
    request.timezone['offset'] = int(request.POST['timezone_offset'])
    request.session['timezone'] = request.timezone
    return shortcuts.redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def fan(request, action, model_class, model_pk, app_name='gsm'):
    model_class = models.get_model(app_name, model_class)
    model = shortcuts.get_object_or_404(model_class, pk=model_pk)
    if action == 'become':
        model.fans.add(request.user)
        actstream.action.send(request.user, verb='bets on',
            action_object=model)
        message = _('you indicated that you bet on') + ' %s' % model
    else:
        model.fans.remove(request.user)
        actions = Action.objects.filter(
            actor_content_type = ContentType.objects.get_for_model(User),
            actor_object_id = request.user.pk,
            verb='bets on',
            action_object_content_type = ContentType.objects.get_for_model(model_class),
            action_object_object_id = model_pk
        )
        # ensure triggering of *_delete signals
        for action in actions:
            action.delete()
        message = _('you indicated that you do not bet anymore on') + ' %s' % model
    messages.success(request, message)
    return shortcuts.redirect(model.get_absolute_url())

def sport_json_competitions(request):
    if not request.GET.get('sport', False):
        return http.HttpResponseBadRequest()
    sport = shortcuts.get_object_or_404(Sport, pk=request.GET['sport'])
    data = [[c.pk, c.name] for c in sport.get_active_competitions()]
    return http.HttpResponse(simplejson.dumps(data))

def sport_json_sessions(request):
    if not request.GET.get('sport', False):
        return http.HttpResponseBadRequest()
    sport = shortcuts.get_object_or_404(Sport, pk=request.GET['sport'])
    qs = Session.objects.filter(datetime_utc__gte=datetime.date.today())
    competition = request.GET.get('competition', False)
    if competition:
        qs = qs.filter(season__competition__pk=competition)
    data = [[c.pk, c.name] for c in qs]
    return http.HttpResponse(simplejson.dumps(data))

def person_detail_tab(request, sport, gsm_id, tab, tag='person',
    update=False,
    template_name='', extra_context=None):
    sport = get_sport_or_404(sport)

    gsm_entity_class = model_class_for_tag(tag)
    person, created = gsm_entity_class.objects.get_or_create(
        sport = sport,
        tag = tag,
        gsm_id = gsm_id
    )
    context = {
        'sport': sport,
        'language': get_language_from_request(request),
        'person': person,
        'tab': tab,
    }

    if sport.slug == 'tennis':
        t = gsm.get_tree(context['language'], sport, 'get_players', 
            type='player', id=person.gsm_id, detailed='yes')
    else:
        t = gsm.get_tree(context['language'], sport, 'get_career', 
            type='player', id=person.gsm_id, detailed='yes')
    person.element = t.getroot().getchildren()[1]

    if created:
        person.name = unicode(person)
        person.save()

    if tab == 'picks':
        context['bet_list_helper'] = BetListHelper(request, exclude_columns=['support'], **{tag:person})

    template_name = [
        'gsm/%s/%s/%s.html' % (sport.slug, 'person', tab),
        'gsm/%s/%s.html' % ('person', tab),
    ]

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def session_detail_tab(request, sport, gsm_id, tab, tag='match',
    update=False,
    template_name='', extra_context=None):
    sport = get_sport_or_404(sport)

    gsm_entity_class = model_class_for_tag(tag)
    session = shortcuts.get_object_or_404(Session,
        sport=sport, gsm_id=gsm_id)

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
        'session': session,
        'tab': tab,
    }

    t = gsm.get_tree(context['language'], sport, 'get_matches', 
        type='match', id=session.gsm_id, detailed='yes')
    c = t.getroot().getchildren()[1]
    while c.tag != 'match':
        c = c.getchildren()[0]
    session.element = c

    try:
        t = gsm.get_tree(context['language'], sport, 'get_match_statistics', 
            id=session.gsm_id)
        if t != False:
            c = t.getroot().getchildren()[1]
            while c.tag != 'match':
                c = c.getchildren()[0]
            context['statistics'] = statistics = c
    except gsm.GsmException:
        pass

    if tab == 'picks':
        context['bet_list_helper'] = BetListHelper(request, session=session, exclude_columns=['support'])

    template_name = [
        'gsm/%s/%s/%s.html' % (sport.slug, 'session', tab),
        'gsm/%s/%s.html' % ('session', tab),
    ]

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def competition_detail_tab(request, sport, gsm_id, tab, tag='competition',
    update=False,
    template_name='', extra_context=None):
    sport = get_sport_or_404(sport)
    gsm_entity_class = model_class_for_tag(tag)
    competition = shortcuts.get_object_or_404(gsm_entity_class,
        sport=sport, tag=tag, gsm_id=gsm_id)
    
    context = {
        'sport': sport,
        'language': get_language_from_request(request),
        'competition': competition,
        'tab': tab,
    }

    template_name = [
        'gsm/%s/%s/%s.html' % (sport.slug, tag, tab),
        'gsm/%s/%s.html' % (tag, tab),
    ]

    context['cup'] = cup = False
    if competition.get_last_season().round_set.filter(round_type='cup').count():
        cup = context['cup'] = True

    if tab == 'calendar':
        season = competition.get_last_season()
        if cup or season.round_set.count() > 1:
            round_pk = request.GET.get('round', False)
            if round_pk:
                context['round'] = season.round_set.get(pk=round_pk)
            else:
                context['round'] = season.get_current_round()
            context['sessions'] = context['round'].session_set.all()
        elif season.get_current_gameweek():
            gameweek = context['gameweek'] = int(request.GET.get('gameweek', season.get_current_gameweek()))
            context['sessions'] = season.session_set.filter(gameweek=gameweek)
        else:
            if season.session_set.count():
                season_round = season.round_set.all()[0]

                this_week_monday = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
                # start_date should be a monday
                start_date = season_round.start_date - datetime.timedelta(season_round.start_date.weekday())
                dates = rrule(WEEKLY, dtstart=start_date, until=season_round.end_date)

                week = request.GET.get('week', False)
                if not week:
                    default_week = True
                    week = 0
                    for date in dates:
                        if date == this_week_monday:
                            break
                        week += 1
                    try:
                        dates[week]
                    except IndexError:
                        week = week - 1
                else:
                    default_week = False

                week = int(week) 
                try:
                    dates[week+1]
                    context['next_week'] = week + 1
                except IndexError:
                    pass
                context['previous_week'] = week - 1

                context['sessions'] = season.session_set.filter(datetime_utc__gte=dates[week]).filter(datetime_utc__lte=dates[week] + datetime.timedelta(7))

                if not context['sessions'].count() and default_week:
                    week -= 1
                    context['previous_week'] -= 1
                    context['sessions'] = season.session_set.filter(datetime_utc__gte=dates[week]).filter(datetime_utc__lte=dates[week] + datetime.timedelta(7))

                context['last_sessions'] = season.session_set.filter(datetime_utc__gte=datetime.date.today() - datetime.timedelta(7)).filter(status='Played')
                context['next_sessions'] = season.session_set.filter(datetime_utc__lte=datetime.date.today() + datetime.timedelta(7)).filter(status='Fixture')
            else:
                context['sessions'] = None

    if sport.slug == 'tennis':
        season = competition.get_last_season()
        seasons = competition.season_set.filter(end_date=season.end_date)
        context['rankings_trees'] = trees = []
        for season in seasons:
            if season.season_type == 'double':
                trees.append({
                    'tree': gsm.get_tree(context['language'], sport, 
                        'get_rankings', type=season.season_type,
                        tour_id=competition.championship.gsm_id),
                    'season': season,
                })
            else:
                trees.append({
                    'tree': gsm.get_tree(context['language'], sport, 
                        'get_rankings', type=season.season_type, 
                        tour_id=competition.championship.gsm_id),
                    'season': season,
                })

    if tab == 'picks':
        context['bet_list_helper'] = BetListHelper(request, session__season__competition=competition, exclude_columns=['support'])
    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def team_detail_tab(request, sport, gsm_id, tab, tag='team',
    update=False,
    template_name='', extra_context=None):
    sport = get_sport_or_404(sport)
    gsm_entity_class = model_class_for_tag(tag)
    team = shortcuts.get_object_or_404(gsm_entity_class,
        sport=sport, tag=tag, gsm_id=gsm_id)

    context = {
        'sport': sport,
        'language': get_language_from_request(request),
        'team': team,
        'tab': tab,
    }

    tree = gsm.get_tree(context['language'], sport, 'get_teams', 
        type='team', id=team.gsm_id, detailed='yes')
    team.element = tree.getroot().findall('team')[0]
    team.name = team.element.attrib['official_name']

    template_name = [
        'gsm/%s/%s/%s.html' % (sport.slug, tag, tab),
        'gsm/%s/%s.html' % (tag, tab),
    ]

    def get_reference_season(team):
        # find reference seasons for stats
        q = Season.objects.filter(sport=sport)

        if 'type' in team.attrib.keys() and team.attrib['type']:
            if team.attrib['type'] == 'club':
                q = q.filter(competition__competition_type='club')
                if q.filter(competition__competition_format=u'Domestic league').count():
                    q = q.filter(competition__competition_format=u'Domestic league')
                else:
                    q = q.filter(competition__important=True)
            if team.attrib['type'] == 'national':
                q = q.filter(competition__competition_type='international')

        # exclude friendlies
        q = q.exclude(competition__name_en='Friendlies')

        # exclude seasons in which team is not participating
        q = q.filter(Q(session__oponnent_A=team)|Q(session__oponnent_B=team)).distinct()

        # any ongoing season ?
        today = datetime.date.today()
        ongoing = q.filter(end_date__gte=today, start_date__lte=today).count()
        if ongoing == 1:
            return q.get(end_date__gte=today, start_date__lte=today)
        elif q.filter(end_date__lte=today).order_by('-end_date').count():
            return q.filter(end_date__lte=today).order_by('-end_date')[0]
        elif q.count():
            return q.order_by('end_date')[0]
        else:
            return False

    def get_resultstable_for_season(season, team):
        # get stats
        tree = gsm.get_tree(context['language'], sport,
            'get_tables', id=season.gsm_id, type='season')
        group_elements = tree.findall('competition/season/round/group')
        resultstable_elements = tree.findall('competition/season/round/resultstable')
        if group_elements and not resultstable_elements:
            for group_element in group_elements:
                for ranking_element in group_element.findall('resultstable/ranking'):
                    if ranking_element.attrib['team_id'] == str(team.gsm_id):
                        resultstable_elements = group_element
                        break

        for resultstable in resultstable_elements:
            if resultstable.attrib['type'] == 'total':
                return resultstable

    if tab == 'home':
        # find next sessions
        q = Session.objects.filter(sport=sport)
        q = q.filter(Q(oponnent_A=team)|Q(oponnent_B=team))

        q_played = q.filter(status='Played').order_by(
            '-datetime_utc').values_list('pk', flat=True).distinct()[:2]
        q_next = q.filter(status__in=('Playing', 'Suspended', 'Fixture')).order_by(
            'datetime_utc').filter(datetime_utc__gte=datetime.date.today()).distinct().values_list('pk', flat=True)[:2]
        context['next_sessions'] = Session.objects.filter(pk__in=list(q_played)+list(q_next)).order_by('datetime_utc')

        reference_season = context['reference_season'] = get_reference_season(team)
        if reference_season:
            context['resultstable'] = get_resultstable_for_season(reference_season, team)

    elif tab == 'squad':
        # season filter
        context['team_seasons'] = Season.objects.filter(
            Q(round__session__in=team.sessions_as_A.all()) |
            Q(round__session__in=team.sessions_as_B.all())
        ).distinct().order_by('name')
        if 'season_gsm_id' in request.GET and request.GET['season_gsm_id']:
            season = shortcuts.get_object_or_404(Season, gsm_id=request.GET['season_gsm_id'], 
                sport=sport)
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

        # person orderer
        positions = {}
        for person_element in team_element.findall('person'):
            if person_element.attrib['type'] in ('player', 'Joueur', 'Player'):
                if 'position' not in person_element.attrib.keys():
                    position = _('player')
                else:
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

        order = (
            'Goalkeeper',
            'Defender',
            'Midfielder',
            'Attacker',
        )
        ordered_positions = OrderedDict()
        for key in order:
            if key in positions.keys():
                ordered_positions[key] = positions.pop(key)
        for key, value in positions.items():
            # copy what's left
            ordered_positions[key] = value

        context['positions'] = ordered_positions
    elif tab == 'statistics':
        reference_season = get_reference_season(team)
        context['reference_season'] = reference_season
        if reference_season:
            context['resultstable'] = get_resultstable_for_season(reference_season, team)
    elif tab == 'picks':
        context['bet_list_helper'] = x= BetListHelper(request, team=team, exclude_columns=['support'])

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))

def entity_list(request, sport, tag, 
    update=False,
    template_name='', extra_context=None):

    sport = get_sport_or_404(sport)

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

    sport = get_sport_or_404(sport)

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
    if gsm_entity_class in (Session, Competition):
        return http.HttpResponseNotFound()
    
    entity = shortcuts.get_object_or_404(gsm_entity_class,
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
    sport = get_sport_or_404(sport)
    return shortcuts.redirect(sport.get_matches_absolute_url())

def sport_detail_tab(request, sport, tab,
    template_name='', extra_context=None):
    sport = get_sport_or_404(sport)

    template_name = (
        template_name,
        'gsm/%s/%s.html' % (sport.slug, tab),
        'gsm/sport/%s.html' % tab,
    )

    context = {
        'tab': tab,
        'sport': sport,
        'language': get_language_from_request(request),
    }

    sessions_qs = Session.objects.all()
    sessions_qs = sessions_qs.filter(sport=sport)

    if tab == 'matches':
        oneday = datetime.timedelta(days=1)
        context['today'] = today = datetime.date.today()
        context['yesterday'] = today - oneday
        context['tomorrow'] = today + oneday
        sessions_qs = sessions_qs.order_by('season', 'datetime_utc')
        f = SessionFilter(request.GET, sessions_qs)
        context['filter'] = f

    elif tab == 'picks':
        context['bet_list_helper'] = x= BetListHelper(request, 
                                                session__sport=sport, 
                                                exclude_columns=['support'])

    elif tab == 'home':
        sessions_qs = Session.objects.filter(sport=sport, status='Fixture').order_by('datetime_utc')

    context['next_sessions'] = sessions_qs[:4]

    context.update(extra_context or {})
    return shortcuts.render_to_response(template_name, context,
        context_instance=template.RequestContext(request))
