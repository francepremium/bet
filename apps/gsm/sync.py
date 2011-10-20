import datetime

from django.db.models import Max

import gsm

from models import *

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def datetime_to_string(dt):
    return dt.strftime(DATETIME_FORMAT)

def string_to_datetime(s):
    try:
        return datetime.datetime.strptime(s, DATETIME_FORMAT)
    except ValueError:
        return datetime.datetime.strptime(s, '%Y-%m-%d')

class Sync(object):
    def __init__(self, sport, last_updated, minimal_date, logger, 
        cooldown=0, language='en', names_only=False, quiet=False):
        self.sport = sport
        self.minimal_date = minimal_date
        self.language = language
        self.logger = logger
        self.cooldown = cooldown
        self.names_only = names_only
        self.quiet = quiet

        if isinstance(last_updated, str):
            self.last_updated = string_to_datetime(last_updated)
        else:
            self.last_updated = last_updated

        if self.sport.slug == 'tennis':
            self.oponnent_tag = 'person'
        else:
            self.oponnent_tag = 'team'

        self.autocopy = (
            'start_date',
            'end_date'
        )

        self._tag_class_map = {
            'competition': Competition,
            'tour': Championship,
            'season': Season,
            'match': Session,
        }

        self._tag_method_map = {
            'competition': 'get_competitions',
            'tour': 'get_tours',
            'season': 'get_seasons',
            'match': 'get_matches',
        }

    def log(self, level, message):
        if not self.quiet:
            message = u'[%s] ' % self.sport.slug + message.decode('utf-8')
            self.logger.log(getattr(logging, level.upper()), message)

    def get_tree(self, *args, **kwargs):
        kwargs['retry'] = 3000
        kwargs['update'] = True

        return gsm.get_tree(self.language, self.sport, *args, **kwargs
            ).getroot()

    def skip(self, e):
        if e.tag not in self._tag_class_map.keys():
            self.log('debug', 'Skipping tag %s' % e.tag)
            return True

        last_updated = string_to_datetime(e.attrib['last_updated'])
        if last_updated < self.last_updated:
            self.log('debug', 'Skipping because no update %s #%s' % (e.tag, 
                e.attrib.get('%s_id' % e.tag)))
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

        if date and string_to_datetime(date) < self.minimal_date:
            self.log('debug', 'Skipping too old %s #%s' % (e.tag,
                e.attrib.get('%s_id' % e.tag)))
            return True

        self.log('debug', 'Update necessary for %s #%s' % (e.tag,
            e.attrib.get('%s_id' % e.tag)))

    def element_to_model(self, e):
        try:
            return self._tag_class_map[e.tag].objects.get(
                sport=self.sport, gsm_id=e.attrib[e.tag + '_id'],
                tag=e.tag)
        except self._tag_class_map[e.tag].DoesNotExist:
            return self._tag_class_map[e.tag](
                sport=self.sport, gsm_id=e.attrib[e.tag + '_id'],
                tag=e.tag)

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
                    e.attrib['%s_%s_name' % (self.oponnent_tag, X)]))

            setattr(model, 'name_%s' %  self.language, u' vs. '.join(names))

        else:
            raise gsm.GsmException(
                'Cannot find name for sport %s tag %s gsm_id %s' % (
                self.sport.slug, model.tag, model.gsm_id))

    def update(self, e, parent=None):
        model = self.element_to_model(e)
        self.log('debug', 'Updating %s:%s' % (model.tag, model.gsm_id))

        self.set_model_name(model, e)

        if not self.names_only:
            self.set_model_area(model, e)

            for key in self.autocopy:
                if key in e.attrib.keys() and hasattr(model, key):
                    self.copy_attr(model, e, key)

            method_key = model.__class__.__name__.lower()
            method = 'update_%s' % method_key
            if hasattr(self, method):
                getattr(self, method)(model, e, parent)

            method = 'update_%s_%s' % (self.sport.slug, method_key)
            if hasattr(self, method):
                getattr(self, method)(model, e, parent)

        model.save()

        def update_children(e):
            for child in e.getchildren():
                if 'double_A_id' in e.attrib.keys():
                    continue # important !!

                if self.skip(child):
                    update_children(child)
                else:
                    self.update(child, parent=model)
        update_children(e)

        if e.tag == 'season':
            tree = self.get_tree('get_matches', type='season', id=model.gsm_id, detailed='yes')
            for sube in gsm.parse_element_for(tree, 'match'):
                if not self.skip(sube):
                    if 'double_A_id' in sube.attrib.keys():
                        continue # important !!
                    self.update(sube, model)

        time.sleep(self.cooldown)

    def copy_attr(self, model, e, source, destination=None):
        if destination is None:
            destination = source
        
        value = e.attrib.get(source, None) or None

        if str(value) == '4294967295':
            # gsm screwd up again
            return

        setattr(model, destination, value)

    def update_competition(self, model, e, parent=None):
        model.championship = parent

        self.copy_attr(model, e, 'court', 'court_type')
        self.copy_attr(model, e, 'teamtype', 'team_type')
        self.copy_attr(model, e, 'type', 'competition_type')
        self.copy_attr(model, e, 'format', 'competition_format')

        if not model.display_order:
            model.display_order = Competition.objects.filter(sport=self.sport
                ).aggregate(Max('display_order'))['display_order__max'] or 0 + 1
    
    def update_season(self, model, e, parent=None):
        model.competition = parent

        self.copy_attr(model, e, 'type', 'season_type')
        self.copy_attr(model, e, 'gender')
        self.copy_attr(model, e, 'prize_money')
        self.copy_attr(model, e, 'prize_currency')
    
    def update_session(self, model, e, parent=None):
        if isinstance(parent, Round):
            model.round = parent
            model.season = parent.season
        elif isinstance(parent, Season):
            model.season = parent

        model.datetime_utc = self.get_session_datetime_utc(e)

        self.copy_attr(model, e, 'status')
        self.copy_attr(model, e, 'gameweek')

        P = self.oponnent_tag
        for X in ('A', 'B'):
            self.copy_attr(model, e, 'fs_%s' % X, '%s_score' % X)
            self.copy_attr(model, e, 'eps_%s' % X, '%s_ets' % X)
            self.copy_attr(model, e, 'ets_%s' % X, '%s_ets' % X)
            self.copy_attr(model, e, 'p1s_%s' % X, '%s1_score' % X)
            self.copy_attr(model, e, 'p2s_%s' % X, '%s2_score' % X)
            self.copy_attr(model, e, 'p3s_%s' % X, '%s3_score' % X)
            self.copy_attr(model, e, 'p4s_%s' % X, '%s4_score' % X)

            if e.attrib['%s_%s_id' % (P, X)]:
                oponnent, created = GsmEntity.objects.get_or_create(
                    sport=self.sport,
                    gsm_id=e.attrib['%s_%s_id' % (P, X)],
                    tag=self.oponnent_tag)

                if created:
                    code = e.attrib.get('%s_%s_country' % (P, X))
                    oponnent.area = Area.objects.get_for_country_code_3(code)
                    self.copy_attr(oponnent, e, '%s_%s_name' % (P, X), 'name')

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
                    '%s%s_score' % (X, i))

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
