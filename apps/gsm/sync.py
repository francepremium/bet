import datetime

import gsm

from models import *

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def datetime_to_string(dt):
    return dt.strftime(DATETIME_FORMAT)

def string_to_datetime(s):
    return datetime.strptime(s, DATETIME_FORMAT)

class Sync(object):
    def __init__(self, sport, last_updated, minimal_date, logger, 
        language='en'):
        self.sport = sport
        self.minimal_date = minimal_date
        self.language = language
        self.logger = logger

        if isinstance(last_updated, str):
            self.last_updated = string_to_datetime(last_updated)
        else:
            self.last_updated = last_updated

        if self.sport.slug == 'tennis':
            self.oponnent_prefix = 'person'
        else:
            self.oponnent_prefix = 'team'

        self.autocopy = (
            'start_date',
            'end_date'
        )

        self._tag_class_map = {
            'competition': Competition,
            'tour': Championship,
            'season': Season,
            'round': Round,
            'match': Session,
        }

        self._tag_method_map = {
            'competition': 'get_competitions',
            'tour': 'get_tours',
            'season': 'get_seasons',
            'round': 'get_rounds',
            'match': 'get_matches',
        }

    def log(self, level, message):
        message = '[%s] ' % self.sport.slug + message
        self.logger.log(level, message)

    def get_tree(self, *args, **kwargs):
        kwargs['retry'] = 3000
        if 'language' in kwargs.keys() and kwargs['language']:
            language = kwargs.pop('language')
        else:
            language = self.language

        if self.last_updated:
            kwargs['last_updated'] = datetime_to_string(self.last_updated)

        return gsm.get_tree(language, self.sport, *args, **kwargs
            ).getroot()

    def skip(self, e):
        if e.tag not in self._tag_class_map.keys():
            self.log('debug', 'Skipping tag %s' % e.tag)
            return

        last_updated = string_to_datetime(e.attrib['last_updated'])
        if last_updated < self.last_updated:
            self.log('debug', 'Update necessary for %s #%s' % (e.tag, 
                e.attrib.get('%s_id' % e.tag))
            return True
        
        date_attrs = [
            'start_date',
            'end_date',
        ]

        date = None
        for key in date_attrs:
            try:
                date = e.attrib.get(key)
                break
            except:
                continue

        if date and string_to_datetime(date) > self.minimal_date:
            return True

    def e_to_model(self, e):
        obj, created = self._tag_class_map[e.tag].objects.get_or_create(
            sport=self.sport, gsm_id=e.attrib[e.tag + '_id'],
            tag=e.tag)
        return obj

    def sync_by_get_seasons(self, e=None):
        root = self.get_tree('get_seasons')

        if not root:
            self.log('error', 'Did not get tree for get_seasons')
            return
        
        for e in root.getchildren():
            if e.tag == 'method' or self.skip(e):
                continue

            if e.tag in self._tag_class_map.keys():
                self.update(e)

    def set_model_area(self, model, e):
        if not hasattr(model, 'area'):
            return

        if 'area_id' not in e.attrib.keys():
            return

        model.area = Area.objects.get_for_gsm_id(e.attrib['area_id'])

    def set_model_name(self, model, e):
        if 'name' in e.attrib.keys():
            setattr(model, 'name_%s' %  self.language, 
                unicode(e.attrib['name']))

        elif isinstance(model, Session):
            names = []
            for X in ('A', 'B'):
                names.append(unicode(
                    e.attrib['%s_%s_name' % self.oponnent_prefix, X]))

            setattr(model, 'name_%s' %  self.language, u' vs. '.join(names))

        else:
            raise gsm.GsmException(
                'Cannot find name for sport %s tag %s gsm_id %s' % (
                self.sport.slug, model.tag, model.gsm_id))

        for code, language in settings.LANGUAGES:
            if code == self.language:
                continue

            tree = self.get_tree(self._tag_method_map[model.tag], 
                language=code)

            for e in gsm.parse_e_for(model.tag):
                setattr(model, 'name_%s' % code, e.attrib['name'])

    def update(self, e):
        self.log('debug', 'Updating %s with %s' % (model, e.attrib))

        model = self.get_or_create(e)
        self.set_model_name(model, e)
        self.set_model_area(model, e)

        for key in self.autocopy:
            if key in e.attrib.keys() and hasattr(model, key):
                self.copy_attr(model, e, key)

        method = 'update_%s' % model.tag.lower()
        if hasattr(self, method):
            getattr(self, method)(self, model, e)

        method = 'update_%s_%s' % (self.sport.slug, model.tag.lower())
        if hasattr(self, method):
            getattr(self, method)(self, model, e)

        model.save()

        def update_children(e):
            for child in e.getchildren():
                if 'double_A_id' in e.attrib.keys():
                    continue # important !!

                if self.skip(child):
                    update_children(child)
                
                self.update(child, parent=model)

        time.sleep(self.cooldown)

    def copy_attr(self, model, e, source, destination=None):
        if destination is None:
            destination = source
        
        value = e.attrib.get(source, None) or None
        setattr(model, destination, value)

    def update_competition(self, model, e, parent=None):
        model.championship = parent

        self.copy_attr(model, e, 'court', 'court_type')
        self.copy_attr(model, e, 'teamtype', 'team_type')
        self.copy_attr(model, e, 'type', 'competition_type')
        self.copy_attr(model, e, 'format', 'competition_format')
    
    def update_season(self, model, e, parent=None):
        model.competition = parent

        self.copy_attr(model, e, 'type', 'season_type')
        self.copy_attr(model, e, 'gender')
        self.copy_attr(model, e, 'prize_money')
        self.copy_attr(model, e, 'prize_currency')
    
    def update_round(self, model, e, parent=None):
        model.season = parent

        model.has_outgroup_matches = e.attrib.get(
            'has_outgroup_matches', 'no') == 'yes'
        
        self.copy_attr(model, e, 'groups')
        self.copy_attr(model, e, 'type', 'round_type')
        self.copy_attr(model, e, 'scoringsystem', 'scoring_system')
    
    def update_session(self, model, e, parent=None):
        if isinstance(parent, Round):
            model.round = parent
            model.season = parent.season
        elif isinstance(parent, Season):
            model.season = parent

        model.datetime_utc = self.get_session_datetime_utc(e)

        self.copy_attr(model, e, 'status')
        self.copy_attr(model, e, 'gameweek')

        P = self.oponnent_prefix
        for X in ('A', 'B'):
            self.copy_attr(model, e, 'fs_%s' % X, '%s_score' % X)
            self.copy_attr(model, e, 'eps_%s' % X, '%s_ets' % X)
            self.copy_attr(model, e, 'ets_%s' % X, '%s_ets' % X)
            self.copy_attr(model, e, 'p1s_%s' % X, '%s1_score' % X)
            self.copy_attr(model, e, 'p2s_%s' % X, '%s2_score' % X)
            self.copy_attr(model, e, 'p3s_%s' % X, '%s3_score' % X)
            self.copy_attr(model, e, 'p4s_%s' % X, '%s4_score' % X)

            oponnent, created = GsmEntity.objects.get_or_create(
                sport=self.sport,
                gsm_id=e.attrib['%s_%s_id'] % (P, X),
                tag='person')

            if created:
                code = e.attrib.get('%s_%s_country' % (P, X))
                oponnent.area = Area.objects.get_for_country_code_3(code)
                self.copy_attr(model, e, 
                oponnent.name = e.attrib.get('%s_%s_name' % (P, X), None)

            setattr(model, 'oponnent_%s' % X, oponnent)

        winner = e.attrib.get('winner', None)
        if winner in ('A', 'B'):
            model.winner = getattr(model, 'oponnent_%s' % e.attrib['winner'])
        elif winner == 'draw':
            model.draw = True

    def update_tennis_session(self, model, e, parent=None):
        i = 1
        for set_element in e.findall('set'):
            for X in ('A', 'B'):
                self.copy_attr(model, set_element, 'score_%s' % X, 
                    '%s%s_score' % (X, i)

            i += 1
            if i > 5:
                break

    def update_soccer_session(self, model, e, parent=None):
        ps_A = e.attrib.get('ps_A', '')
        ps_B = e.attrib.get('ps_B', '')
        if ps_A:
            if ps_A > ps_B:
                model.penalty = 'A'
            else:
                model.penalty = 'B'

    def update_rugby_session(self, model, e, parent=None):
        ps_A = e.attrib.get('sds_A', '')
        ps_B = e.attrib.get('sds_B', '')
        if ps_A:
            if ps_A > ps_B:
                model.penalty = 'A'
            else:
                model.penalty = 'B'
    
    def get_session_datetime_utc(self, e):
        # OMFG GSM SUCKS at datetime consistency !!
        converter = Session._meta.get_field('actual_start_datetime')
        actual_start_datetime = '%s %s' % (
            e.attrib.get('actual_start_date', '') or '',
            e.attrib.get('actual_start_time', '') or '',
        )
        
        if actual_start_datetime[-1] == ' ': # no time, set to midnight
            actual_start_datetime = actual_start_datetime + '00:00:00'

        if actual_start_datetime not in (' ', ' 00:00:00'):
            actual_start_datetime = converter.to_python(actual_start_datetime)
        else:
            actual_start_datetime = None

        if 'official_start_date' in e.attrib.keys():
            official_start_datetime = '%s %s' % (
                e.attrib.get('official_start_date', '') or '',
                e.attrib.get('official_start_time', '00:00:00') or '00:00:00',
            )
        else:
            official_start_datetime = '%s %s' % (
                e.attrib.get('date_utc', '') or '',
                e.attrib.get('time_utc', '00:00:00') or '00:00:00',
            )

        if official_start_datetime[-1] == ' ': # no time, set to midnight
            official_start_datetime = official_start_datetime + '00:00:00'
        if official_start_datetime not in (' ', ' 00:00:00'):
            official_start_datetime = converter.to_python(official_start_datetime)
        else:
            official_start_datetime = None

        return actual_start_datetime or official_start_datetime
