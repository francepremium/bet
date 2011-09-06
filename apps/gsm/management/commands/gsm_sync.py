import logging
import urllib
from datetime import datetime, date, time
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError

from progressbar import ProgressBar

from gsm.models import *
import gsm

logger = logging.getLogger('gsm')
logger.info('starting sync')

class UnexpectedChild(Exception):
    def __init__(self, parent, child):
        msg = 'Tag %s was found in %s' % (child.tag, parent.tag)
        super(UnexpectedChild, self).__init__(msg)

class Command(BaseCommand):
    args = 'n/a'
    help = 'sync database against gsm'

    def handle(self, *args, **options):
        self.cooldown = options.get('cooldown', 0)

        self.areas_country_code_2()

        for code, language in settings.LANGUAGES:
            root = gsm.get_tree(code, 'soccer', 'get_areas').getroot()
            for element in root.getchildren():
                if element.tag == 'area':
                    self.save_area(code, element)
    
            for sport in Sport.objects.all():
                logger.debug("Saving seasons for %s" % sport)
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
                    
                    time.sleep(self.cooldown)

        logger.info('done sync')

    def areas_country_code_2(self):
        tmpfile, message = urllib.urlretrieve('http://www.andrewpatton.com/countrylist.csv')
        fh = open(tmpfile)
        fh.readline() # skip csv header
        for line in fh.readlines():
            row = line.split(',')
            if not row[11][1:-1]: # skip empty codes
                continue
            try:
                area = Area.objects.get(country_code__iexact=row[11][1:-1])
            except Area.DoesNotExist:
                continue

            area.country_code_2 = country_code=row[10][1:-1].lower()
            area.save()
        fh.close()

    def update_model(self, model_class, unique_properties, properties):
        changed = {}

        try:
            model = model_class.objects.get(**unique_properties)
        except model_class.DoesNotExist:
            model = model_class(**unique_properties)
        
        for k, v in properties.items():
            if not hasattr(model_class, k):
                if getattr(model, k) != getattr(model, '_meta').get_field(k).to_python(v):
                    changed[k] = 'normal val %s: %s != %s' % (k, getattr(model, k), getattr(model, '_meta').get_field(k).to_python(v))
                    setattr(model, k, v)
            else: # handle relations
                if v is None:
                    if getattr(model, '%s_id' % k) != None:
                        changed[k] = 'none relation %s: %s != %s' % (k, getattr(model, '%s_id' % k), v)
                        setattr(model, k, v)
                elif getattr(model, '%s_id' % k) != v.pk:
                    changed[k] = 'relation %s: %s != %s' % (k, getattr(model, '%s_id' % k), v.pk)
                    setattr(model, k, v)

        if changed:
            logger.debug('- - - %s changed or created', self.entity_to_text(model))

            invalid = []
            for k, v in changed.items():
                logger.debug(v)
                if '4294967295' in v:
                    invalid.append(k)
            for k in invalid:
                setattr(model, k, None)
                logger.warning("  FIXED INVALID" +  changed[k] + ' GSM_ID %s' % model.gsm_id)

            try:
                model.save()
                logger.debug('- - - Saved %s' % self.entity_to_text(model))
            except:
                logger.error("- - - Could not save %s" % self.entity_to_text(model))
        
        return model

    def entity_to_text(self, entity):
        if isinstance(entity, Area):
            return u'Area %s: %s' % (entity.pk, entity)
        else:
            return u'%s, %s, %s' % (entity.sport, entity.tag, entity.gsm_id)

    def save_area(self, language, element, **properties):
        properties.update({
            'name_%s' % language: unicode(element.attrib['name']),
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

    def save_championship(self, language, sport, element, **properties):
        properties.update({
            'name_%s' % language: unicode(element.attrib['name']),
            'last_updated': element.attrib['last_updated'],
        })

        championship = self.update_model(   
            Championship, 
            {
                'gsm_id': element.attrib.get('tour_id', None) or element.attrib.get('championship_id'),
                'sport': sport,
                'tag': element.tag,
            },
            properties
        )
        
        for child in element.getchildren():
            if child.tag == 'competition':
                self.save_competition(language, sport, child, championship=championship)

    def save_competition(self, language, sport, element, **properties):
        properties.update({
            'name_%s' % language: unicode(element.attrib['name']),
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
                'tag': element.tag,
            },
            properties
        )

        for child in element.getchildren():
            if child.tag == 'season':
                self.save_season(language, sport, child, competition=competition)
            else:
                raise UnexpectedChild(element, child)
                    
            time.sleep(self.cooldown)

    def save_season(self, language, sport, element, **properties):
        properties.update({
            'name_%s' % language: unicode(element.attrib['name']),
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
                'tag': element.tag,
            },
            properties
        )

        # save teams: actually we ain't
        #if sport.slug in ('rugby', 'basketball', 'soccer'):
            #root = gsm.get_tree(language, sport, 'get_teams', 
                #detailed=True, type='saeson', id=season.gsm_id).getroot()
            #for team_element in root.findall('team'):
                #self.save_team(language, sport, team_element)

        if sport.slug == 'motorsports': # directly handle sessions
            root = gsm.get_tree(language, sport, 'get_sessions', 
                type='season', id=season.gsm_id).getroot()
            for session_element in root.findall('championship/competition/season/session'):
                self.save_session(language, sport, session_element, season=season)
                time.sleep(self.cooldown)
        else: # handle rounds
            if sport.slug == 'tennis':
                root = gsm.get_tree(language, sport, 'get_matches', 
                    type='season', id=season.gsm_id, detailed='yes').getroot()
            else:
                root = gsm.get_tree(language, sport, 'get_matches', 
                    type='season', id=season.gsm_id).getroot()

            rounds = root.findall('competition/season/round')
            if not rounds:
                rounds = root.findall('tour/competition/season/round')

            for round_element in rounds:
                self.save_round(language, sport, round_element, season=season)
                time.sleep(self.cooldown)

    def save_team(self, language, sport, element, **properties):
        if element.attrib.get('area_id', False):
            area = Area.objects.get(gsm_id=element.attrib['area_id'])
        else:
            area = None

        properties.update({
            'name_%s' % language: unicode(element.attrib.get('official_name')),
            'area': area,
        })

        # actually we ain't doing that yet because features won't be even between sports

    def save_round(self, language, sport, element, **properties):
        has_outgroup_matches = element.attrib.get('has_outgroup_matches', 'no') == 'yes'
        properties.update({
            'name_%s' % language: unicode(element.attrib.get('name', element.attrib.get('title'))),
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
                'tag': element.tag,
            },
            properties
        )

        # 3 fucking structures, just for 2 soccer competitions
        matches = element.findall('match')
        if matches:
            for match in matches:
                self.save_session(language, sport, match, session_round=r, season=r.season)
                time.sleep(self.cooldown)

        matches = element.findall('group/match')
        if matches:
            for match in matches:
                self.save_session(language, sport, match, session_round=r, season=r.season)
                time.sleep(self.cooldown)

        matches = element.findall('aggr/match')
        if matches:
            for match in matches:
                self.save_session(language, sport, match, session_round=r, season=r.season)
                time.sleep(self.cooldown)

    def save_session(self, language, sport, element, **properties):
        converter = Session._meta.get_field('actual_start_datetime')
        actual_start_datetime = '%s %s' % (
            element.attrib.get('actual_start_date', '') or '',
            element.attrib.get('actual_start_time', '') or '',
        )
        
        if actual_start_datetime[-1] == ' ': # no time, set to midnight
            actual_start_datetime = actual_start_datetime + '00:00:00'

        if actual_start_datetime not in (' ', ' 00:00:00'):
            actual_start_datetime = converter.to_python(actual_start_datetime)
        else:
            actual_start_datetime = None

        if 'official_start_date' in element.attrib.keys():
            official_start_datetime = '%s %s' % (
                element.attrib.get('official_start_date', '') or '',
                element.attrib.get('official_start_time', '00:00:00') or '00:00:00',
            )
        else:
            official_start_datetime = '%s %s' % (
                element.attrib.get('date_utc', '') or '',
                element.attrib.get('time_utc', '00:00:00') or '00:00:00',
            )

        if official_start_datetime[-1] == ' ': # no time, set to midnight
            official_start_datetime = official_start_datetime + '00:00:00'
        if official_start_datetime not in (' ', ' 00:00:00'):
            official_start_datetime = converter.to_python(official_start_datetime)
        else:
            official_start_datetime = None

        properties.update({
            'status': element.attrib.get('status'),
            'gameweek': element.attrib.get('gameweek') or None,
            'last_updated': element.attrib.get('last_updated', None),
            'datetime_utc': actual_start_datetime or official_start_datetime,
        })

        if not element.attrib.get('time_utc') and not element.attrib.get('official_start_time'):
            properties['time_unknown'] = True

        oponnent_names = {
            'A': u'?',
            'B': u'?',
        }
        xml_map = (
            ('person_%s_name', 'person'),
            ('team_%s_name', 'team'),
        )
        for x in ('A', 'B'):
            for attr, tag in xml_map:
                xattr = attr % x
                i = element.attrib.get(xattr, False)
                if i:
                    oponnent_names[x] = unicode(i)

        xml_map = (
            ('person_%s_id', 'person'),
            ('double_%s_id', 'double'),
            ('team_%s_id', 'team'),
        )
        for attr, tag in xml_map:
            for x in ('A', 'B'):
                xattr = attr % x
                i = element.attrib.get(xattr, False)
                if i:
                    properties['oponnent_%s' % x], created = GsmEntity.objects.get_or_create(
                        sport=sport, gsm_id=i, tag=tag)
                    changed = False
                    try:
                        area = Area.objects.get(country_code=element.attrib.get(xattr.replace('id', 'country')))
                        if area != properties['oponnent_%s' % x].area:
                            properties['oponnent_%s' % x].area = area
                            changed = True
                    except:
                        pass
                    name = oponnent_names[x]
                    if name != getattr(properties['oponnent_%s' % x], 'name_%s' % language) or changed:
                        setattr(properties['oponnent_%s' % x], 'name_%s' % language, name)
                        properties['oponnent_%s' % x].save()

        if 'A' in element.attrib.get('winner', ''):
            properties['winner'] = properties['oponnent_A']
        elif 'B' in element.attrib.get('winner', ''):
            properties['winner'] = properties['oponnent_B']
        elif element.attrib.get('winner', '') == 'draw':
            properties['draw'] = True

        if sport.slug == 'tennis':
            i = 1
            for set_element in element.findall('set'):
                properties['A%s_score' % i] = set_element.attrib.get('score_A', None) or None
                properties['B%s_score' % i] = set_element.attrib.get('score_B', None) or None
                i += 1
                if i > 5:
                    break
        elif sport.slug == 'basketball':
            properties['A1_score'] = element.attrib.get('p1s_A', None) or None
            properties['A2_score'] = element.attrib.get('p2s_A', None) or None
            properties['A3_score'] = element.attrib.get('p3s_A', None) or None
            properties['A4_score'] = element.attrib.get('p4s_A', None) or None
            properties['A5_score'] = element.attrib.get('eps_A', None) or None
            properties['B1_score'] = element.attrib.get('p1s_B', None) or None
            properties['B2_score'] = element.attrib.get('p2s_B', None) or None
            properties['B3_score'] = element.attrib.get('p3s_B', None) or None
            properties['B4_score'] = element.attrib.get('p4s_B', None) or None
            properties['B5_score'] = element.attrib.get('eps_B', None) or None
            properties['A_score'] = element.attrib.get('fs_A', None) or None
            properties['B_score'] = element.attrib.get('fs_B', None) or None
            properties['A_ets'] = element.attrib.get('eps_A', None) or None
            properties['B_ets'] = element.attrib.get('eps_B', None) or None
        elif sport.slug == 'soccer':
            properties['A_score'] = element.attrib.get('fs_A', None) or None
            properties['B_score'] = element.attrib.get('fs_B', None) or None
            properties['A_ets'] = element.attrib.get('ets_A', None) or None
            properties['B_ets'] = element.attrib.get('ets_B', None) or None
            ps_A = element.attrib.get('ps_A', '')
            ps_B = element.attrib.get('ps_B', '')
            if ps_A:
                if ps_A > ps_B:
                    properties['penalty'] = 'A'
                else:
                    properties['penalty'] = 'B'
        elif sport.slug == 'rugby':
            properties['A1_score'] = element.attrib.get('p1s_A', None) or None
            properties['A2_score'] = element.attrib.get('p2s_A', None) or None
            properties['B1_score'] = element.attrib.get('p1s_B', None) or None
            properties['B2_score'] = element.attrib.get('p2s_B', None) or None
            properties['A_score'] = element.attrib.get('fs_A', None) or None
            properties['B_score'] = element.attrib.get('fs_B', None) or None
            properties['A_ets'] = element.attrib.get('ets_A', None) or None
            properties['B_ets'] = element.attrib.get('ets_B', None) or None
            sds_A = element.attrib.get('sds_A', '')
            sds_B = element.attrib.get('sds_B', '')
            if sds_A:
                if sds_A > sds_B:
                    properties['penalty'] = 'A'
                else:
                    properties['penalty'] = 'B'

        properties['name_%s' % language] = u'%s vs. %s' % (oponnent_names['A'], oponnent_names['B'])

        session = self.update_model(
            Session,
            {
                'gsm_id': element.attrib.get('match_id'),
                'sport': sport,
                'tag': element.tag,
            },
            properties
        )

