from datetime import datetime, date, time
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError

from progressbar import ProgressBar

from gsm.models import *
import gsm

class UnexpectedChild(Exception):
    def __init__(self, parent, child):
        msg = 'Tag %s was found in %s' % (child.tag, parent.tag)
        super(UnexpectedChild, self).__init__(msg)

class Command(BaseCommand):
    args = 'n/a'
    help = 'sync database against gsm'

    def handle(self, *args, **options):
        for code, language in settings.LANGUAGES:
            #root = gsm.get_tree(code, 'soccer', 'get_areas').getroot()
            #for element in root.getchildren():
                #if element.tag == 'area':
                    #self.save_area(code, element)

            for sport in Sport.objects.all():
                print "Saving seasons for %s" % sport
                properties = {}

                root = gsm.get_tree(code, sport, 'get_seasons', **properties).getroot()

                for element in root.getchildren():
                    if element.tag == 'method':
                        continue
                    elif element.tag in ('tour', 'championship'):
                        self.save_championship(code, sport, element)
                    elif element.tag == 'competition':
                        self.save_competition(code, sport, element)
                    else:
                        raise UnexpectedChild(root, element)

    def update_model(self, model_class, unique_properties, properties):
        changed = []

        try:
            model = model_class.objects.get(**unique_properties)
        except model_class.DoesNotExist:
            model = model_class(**unique_properties)

        for k, v in properties.items():
            if not hasattr(model_class, k):
                if getattr(model, k) != getattr(model, '_meta').get_field(k).to_python(v):
                    changed.append('normal val %s: %s != %s' % (k, getattr(model, k), getattr(model, '_meta').get_field(k).to_python(v)))
                    setattr(model, k, v)
            else: # handle relations
                if v is None:
                    if getattr(model, '%s_id' % k) != None:
                        changed.append('none relation %s: %s != %s' % (k, getattr(model, '%s_id' % k), v))
                        setattr(model, k, v)
                elif getattr(model, '%s_id' % k) != v.pk:
                    changed.append('relation %s: %s != %s' % (k, getattr(model, '%s_id' % k), v.pk))
                    setattr(model, k, v)

        if changed:
            print "CHANGED %s #%s: %s" % (model.__class__, model.gsm_id, "\n".join(changed))
            model.save()
        
        return model

    def save_championship(self, language, sport, element, **properties):
        properties.update({
            'name_%s' % language: element.attrib['name'],
            'last_updated': element.attrib['last_updated'],
        })

        championship = self.update_model(   
            Championship, 
            {
                'gsm_id': element.attrib.get('tour_id', None) or element.attrib.get('championship_id'),
                'sport': sport,
            },
            properties
        )
        
        for child in element.getchildren():
            if child.tag == 'competition':
                self.save_competition(language, sport, child, championship=championship)

    def save_competition(self, language, sport, element, **properties):
        properties.update({
            'name_%s' % language: element.attrib['name'],
            'area': Area.objects.get(gsm_id=element.attrib['area_id']),
            'court_type': element.attrib.get('court', None),
            'team_type': element.attrib.get('teamtype', None),
            'competition_type': element.attrib.get('type', None),
            'competition_format': element.attrib.get('format', None),
            'last_updated': element.attrib['last_updated'],
            'display_order': element.attrib.get('display_order', None),
        })

        competition = self.update_model(
            Competition,
            {
                'gsm_id': element.attrib['competition_id'],
                'sport': sport,
            },
            properties
        )

        for child in element.getchildren():
            if child.tag == 'season':
                self.save_season(language, sport, child, competition=competition)
            else:
                raise UnexpectedChild(element, child)

    def save_season(self, language, sport, element, **properties):
        properties.update({
            'name_%s' % language: element.attrib['name'],
            'season_type': element.attrib.get('type', None) or None,
            'gender': element.attrib.get('gender', None) or None,
            'prize_money': element.attrib.get('prize_money', None) or None,
            'prize_currency': element.attrib.get('prize_currency', None) or None,
            'last_updated': element.attrib.get('last_updated', None) or None,
            'start_date': element.attrib.get('start_date', None) or None,
            'end_date': element.attrib.get('end_date', None) or None,
        })

        season = self.update_model(
            Season,
            {
                'gsm_id': element.attrib['season_id'],
                'sport': sport,
            },
            properties
        )

        if sport.name == 'motorsports': # directly handle sessions
            root = gsm.get_tree(language, sport, 'get_sessions', 
                type='season', id=season.gsm_id).getroot()
            for session_element in root.findall('championship/competition/season/session'):
                self.save_session(language, sport, session_element, season=season)
        else: # handle rounds
            root = gsm.get_tree(language, sport, 'get_matches', 
                type='season', id=season.gsm_id).getroot()

            rounds = root.findall('competition/season/round')
            if not rounds:
                rounds = root.findall('tour/competition/season/round')

            for round_element in rounds:
                self.save_round(language, sport, round_element, season=season)

        if sport.name == 'soccer':
            root = gsm.get_tree(language, sport, 'get_teams', 
                id=season.gsm_id, type='season', detailed='yes').getroot()
            for team_element in root.findall('team'):
                team = self.save_team(language, sport, team_element)
                team.seasons.add(season)


    def save_team(self, language, sport, element, **properties):
        properties.update({
            'team_type': element.attrib.get('type'),
            'play_type': element.attrib.get('teamtype'),
            'name_%s' % language: element.attrib.get('club_name'),
            'official_name': element.attrib.get('official_name'),
            'area': Area.objects.get(gsm_id=element.attrib.get('area_id')),
            'city': element.attrib.get('city'),
            'url': element.attrib.get('url'),
            'founded': element.attrib.get('founded', None) or None,
            'colors': element.attrib.get('club_colors', None) or None,
            'clothing': element.attrib.get('clothing', None) or None,
            'sponsor': element.attrib.get('sponsor', None) or None,
            'details': element.attrib.get('details', None) or None,
        })

        self.update_model(
            Team,
            {
                'sport': sport,
                'gsm_id': element.attrib['gsm_id'],
            },
            properties
        )

    def save_round(self, language, sport, element, **properties):
        has_outgroup_matches = element.attrib.get('has_outgroup_matches', 'no') == 'yes'
        properties.update({
            'name_%s' % language: element.attrib.get('name', element.attrib.get('title')),
            'last_updated': element.attrib.get('last_updated', None) or None,
            'start_date': element.attrib.get('start_date', None) or None,
            'end_date': element.attrib.get('end_date', None) or None,
            'groups': element.attrib['groups'],
            'round_type': element.attrib.get('type', None),
            'scoring_system': element.attrib.get('socringsystem', None),
            'has_outgroup_matches': has_outgroup_matches,
        })

        r = self.update_model(
            Round, 
            {
                'gsm_id': element.attrib['round_id'],
                'sport': sport,
            },
            properties
        )

        for match in element.findall('match'):
            print match.attrib
            self.save_session(language, sport, match, session_round=r)

    def save_session(self, language, sport, element, **properties):
        converter = Session._meta.get_field('actual_start_datetime')
        actual_start_datetime = '%s %s' % (
            element.attrib.get('actual_start_date', '') or '',
            element.attrib.get('actual_start_time', '') or '',
        )
        if actual_start_datetime != ' ':
            actual_start_datetime = converter.to_python(actual_start_datetime)
        else:
            actual_start_datetime = None


        if 'official_start_datetime' in element.attrib.keys():
            official_start_datetime = '%s %s' % (
                element.attrib.get('official_start_date', '') or '',
                element.attrib.get('official_start_time', '00:00:00'),
            )
        else:
            official_start_datetime = '%s %s' % (
                element.attrib.get('date_utc', '') or '',
                element.attrib.get('time_utc', '00:000:00'),
            )

        if official_start_datetime != ' ':
            official_start_datetime = converter.to_python(official_start_datetime)
        else:
            official_start_datetime = None

        properties.update({
            'actual_start_datetime': actual_start_datetime,
            'status': element.attrib.get('status'),
            'gameweek': element.attrib.get('gameweek'),
            'last_updated': element.attrib.get('last_updated', None),
            'score_A': element.attrib.get('score_A', None) or None,
            'score_B': element.attrib.get('score_B', None) or None,
            'datetime_utc': official_start_datetime,
        })

        if element.attrib.get('person_A', False):
            properties['person_A'] = Person.objects.get(
                sport=sport, gsm_id=element.attrib['gsm_id'])
        if element.attrib.get('person_B', False):
            properties['person_B'] = Person.objects.get(
                sport=sport, gsm_id=element.attrib['gsm_id'])


        session = self.update_model(
            Session,
            {
                'gsm_id': element.attrib.get('match_id'),
                'sport': sport,
            },
            properties
        )

        for tennis_set in element.findall('set'):
            print tennis_set.attrib

    def save_area(self, language, element, **properties):
        properties.update({
            'name_%s' % language: element.attrib['name'],
            'country_code': element.attrib['countrycode'],
        })

        area = self.update_model(
            Area, 
            {
                'gsm_id': element.attrib['area_id'],
            },
            properties
        )

        for child in element.getchildren():
            if child.tag == 'area':
                self.save_area(language, child, parent=area)
            else:
                raise UnexpectedChild(element, child)
        
        # saving tennis players is more performent per area
        tennis = Sport.objects.get(name='tennis')
        root = gsm.get_tree(language, tennis, 'get_players', type='area', id=element.attrib['area_id'])
        for person_element in root.findall('person'):
            self.save_person(language, tennis, person_element, area=area)

    def save_person(self, language, sport, element, **properties):
        birth = element.attrib['date_of_birth']
        if birth == '0000-00-00' or not birth: 
            birth = None

        properties.update({
            'name': element.attrib.get('matchname', element.attrib.get('name')),
            'last_updated': element.attrib.get('last_updated', None) or None,
            'first_name': element.attrib.get('firstname'),
            'last_name': element.attrib.get('lastname'),
            'birth': birth,
            'gender': element.attrib['gender'],
            'person_type': element.attrib['type'],
        })

        person = self.update_model(
            Person,
            {
                'gsm_id': element.attrib['person_id'],
                'sport': sport,
            },
            properties
        )

        return person
