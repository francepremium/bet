import re
import datetime

import pytz
from pytz import timezone

from django import template
from django.conf import settings
from django.db.models import Q

import gsm
from gsm.models import GsmEntity, Area, Session, AbstractGsmEntity

register = template.Library()

@register.filter
def session_exists(session):
    return Session.objects.filter(sport=session.sport, gsm_id=session.gsm_id).count()

@register.filter
def goal_column(session, goal):
    event = goal.getchildren()[0]
    if event.attrib['team_id'] == str(session.oponnent_A.gsm_id):
        return 'A'
    elif event.attrib['code'] == 'OG':
        return 'A'
    return 'B'

@register.filter
def is_int(val):
    return val.__class__.__name__ == 'int'

@register.filter
def timezone_adjust(request, value):
    #value = datetime.datetime(value.year, value.month, value.day)
    if hasattr(value, 'tzinfo'):
        local = timezone(settings.TIME_ZONE)
        utc = timezone('UTC')
        value = local.localize(value)
        value = value.astimezone(utc)
        delta = datetime.timedelta(hours=request.timezone.get('offset', 0))
        return value + delta
    else:
        return value

@register.filter
def display_date(date):
    if isinstance(date, str):
        m = re.match(r'(?P<year>[0-9]+)-(?P<month>[0-9]+)-(?P<day>[0-9]+)', 
            date)
        if m:
            return '%s/%s/%s' % (
                m.group('day'),
                m.group('month'),
                m.group('year'),
            )

    if not hasattr(date, 'year'):
        return False

    if datetime.date.today().year == date.year:
        return '%s/%s' % (date.day, date.month)
    else:
        return '%s/%s/%s' % (date.day, date.month, date.year)

@register.filter
def prepend_zero(number):
    number = str(number)
    if len(number) == 1:
        number = '0' + number
    return number

@register.filter
def display_time(time):
    if not hasattr(time, 'hour'):
        return False

    return '%s:%s' % (prepend_zero(time.hour), prepend_zero(time.minute))

@register.filter
def five_sessions_series(team):
    team = GsmEntity.objects.get(gsm_id=team.gsm_id, sport=team.sport, 
        tag=team.tag)
    
    sessions = Session.objects.filter(status='Played').filter(
        Q(oponnent_A=team) |
        Q(oponnent_B=team)
    ).distinct().order_by('-start_datetime')[:5]
    sessions = list(sessions)
    sessions.reverse()

    serie = []
    for session in sessions:
        data = {
            'entity': session,
        }
        if session.draw:
            data['symbol'] = 'D'
        elif session.winner == team:
            data['symbol'] = 'W'
        else:
            data['symbol'] = 'L'
        serie.append(data)

    return serie

@register.filter
def add(value, arg):
    "Subtracts the arg from the value"
    if not arg:
        arg = 0
    if not value:
        value = 0
    return int(value) + int(arg)
add.is_safe = False

@register.filter
def findall(element, path):
    return element.findall(path)

@register.filter
def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)
sub.is_safe = False

@register.filter
def gsm_area_id_flag_url(arg):
    if not arg:
        return False

    if isinstance(arg, int) or (isinstance(arg, str) and arg.isdigit()):
        area = Area.objects.get_for_gsm_id(int(arg))
    elif isinstance(arg, str):
        area = Area.objects.get_for_country_code_3(arg)
    elif isinstance(arg, AbstractGsmEntity):
        area = Area.objects.get_for_object(arg)

    filename = area.country_code_2
    if area.name_en == u'Europe':
        filename = '_European%20Union'
    elif area.name_en == u'N/C America':
        filename = '_CONCACAF'
    elif area.name_en == u'South America':
        filename = '_CSF'
    elif area.name_en in ('England', 'Wales', 'Northern Ireland', 'Scotland'):
        filename = '_' + area.name_en
    elif area.name_en == u'World':
        filename = 'world'

    return '%sflags2/16/%s.png' % (
        settings.STATIC_URL,
        filename,
    )

@register.filter
def age_from_date(date):
    if not date:
        return ''
    birth = datetime.datetime.strptime(date, '%Y-%m-%d')
    delta = datetime.datetime.now() - birth
    return delta.days / 365

@register.inclusion_tag('gsm/_includes/tables_tree.html', takes_context=True)
def gsm_render_tables_tree(context, tree):
    return {
        'sport': context['sport'],
        'language': context['language'],
        'tables_tree': tree,
    }

@register.tag(name='gsm_sessions_render')
def do_gsm_sessions_render(parser, token):
    """
    Takes a Session list.
    """
    split = token.split_contents()
    return GsmSessionsTableNode(*split)

class GsmSessionsTableNode(template.Node):
    def __init__(self, tagname, sessions, divide_by_season=False, fixed_day=False, team=False):
        self.sessions = template.Variable(sessions)
        if team:
            self.team = template.Variable(team)
        else:
            self.team = False
        if divide_by_season:
            self.divide_by_season = template.Variable(divide_by_season)
        if fixed_day:
            self.fixed_day = template.Variable(fixed_day)
    def render(self, context):
        context['sessions'] = self.sessions.resolve(context)
        if hasattr(self.team, 'resolve'):
            context['team'] = self.team.resolve(context)
        if hasattr(self, 'divide_by_season'):
            context['divide_by_season'] = self.divide_by_season.resolve(context)
        if hasattr(self, 'fixed_day'):
            context['fixed_day'] = self.fixed_day.resolve(context)

        if not hasattr(self, 'nodelist'):
            t = template.loader.select_template([
                'gsm/%s/_includes/sessions.html' % context['sport'].slug,
                'gsm/_includes/sessions.html',
            ])
            self.nodelist = t.nodelist
        
        return self.nodelist.render(context)

@register.tag(name='gsm_resultstable_render')
def do_gsm_resultstable_render(parser, token):
    """
    Takes a "resultstable" element, which should contain "ranking" elements.
    The socend argument is a list of columns, ie. 'MP,W,D,L' for:
    | Match played | Win | Draw | Lost |
    """
    split = token.split_contents()
    resultstable_variable = split[1]
    if len(split) > 2:
        columns = split[2]
    else:
        columns = '""'

    return GsmResultsTableNode(resultstable_variable, columns)

class GsmResultsTableNode(template.Node):
    def __init__(self, resultstable, columns):
        self.resultstable = template.Variable(resultstable)
        if columns[0] in ('"', "'"):
            self.columns = columns[1:-1]
        else:
            self.columns = template.Variable(columns)

    def render(self, context):
        context['resultstable'] = self.resultstable.resolve(context)
        if isinstance(self.columns, template.Variable):
            context['columns'] = self.columns.resolve(context).split(',')
        else:
            context['columns'] = self.columns.split(',')

        if not hasattr(self, 'nodelist'):
            t = template.loader.select_template([
                'gsm/%s/_includes/resultstable.html' % context['sport'].slug,
                'gsm/_includes/resultstable.html',
            ])
            self.nodelist = t.nodelist
        
        return self.nodelist.render(context)

@register.tag(name='gsm_tree')
def do_gsm_tree(parser, token):
    """
    Required arguments:
    - method: the API method name
    - key: the context key to set with the resulting ElementTree

    "sport" and "lang" are automatically set from the global context.
    
    Any other argument is passed as API method parameters.

    Example:
    {% gsm_tree key='stats' method='get_match_statistics' id=980534 %}
    Will assign the ElementTree of the follewing url to {{ stats }}
    http://webpull.globalsportsmedia.com/soccer/get_match_statistics?id=980534
    """
    split = token.split_contents()
    kwargs = {}
    for arg in split[1:]:
        equal = arg.find('=')
        if equal:
            kwargs[arg[:equal]] = arg[equal+1:]
        else:
            kwargs[arg] = True
        
    if 'method' not in kwargs:
        raise template.TemplateSyntaxError("gsm_tree requires a method argument (UTSL)")
    if 'key' not in kwargs:
        raise template.TemplateSyntaxError("gsm_tree requires a key argument (UTSL)")
    
    return GsmTreeNode(**kwargs)

class GsmTreeNode(template.Node):
    def __init__(self, **kwargs):
        """ OMG UGLY VOODOO """
        self.arguments = {}

        for k, v in kwargs.items():
            try:
                is_int = str(int(v)) == v
            except:
                is_int = False
            
            if v[0] == '"' or v[0] == "'":
                if k in ('method', 'key'):
                    setattr(self, k, v[1:-1])
                else:
                    self.arguments[k] = v[1:-1]
            elif is_int:
                if k in ('method', 'key'):
                    raise GsmException('Method and key cannot be integers')
                self.arguments[k] = v
            else:
                if k in ('method', 'key'):
                    setattr(self, k, template.Variable(v))
                else:
                    self.arguments[k] = template.Variable(v)

    def render(self, context):
        if hasattr(self.method, 'resolve'):
            method = self.method.resolve(context)
        else:
            method = self.method

        for k, v in self.arguments.items():
            if hasattr(v, 'resolve'):
                self.arguments[k] = v.resolve(context)

        tree = gsm.get_tree(
            context['language'],
            context['sport'],
            method,
            **self.arguments
        )

        if hasattr(self.key, 'resolve'):
            key = self.key.resolve(context)
        else:
            key = self.key

        context[key] = tree

        return ''

@register.tag(name='gsm_entity')
def do_gsm_entity(parser, token):
    """
    Required arguments:
    - key: the context key to set with the resulting GsmEntity
    - (tag and gsm_id) or element:
        - element is an lxml element
        - tag is a gsm tag name (match, season...)
        - gsm_id is the remote id

    Two minimal usage examples:
    
    {% gsm_entity element=foo key=bar %}
    Makes a GsmEntity for element foo, global sport, in {{ bar }}

    {% gsm_entity tag=match gsm_id=123 key=bar %}
    Makes a GsmEntity for tag 'match' with gsm_id 123 in {{ bar }}
    """
    arguments = {}
    for arg in token.split_contents()[1:]:
        equal = arg.find('=')
        if equal:
            arguments[arg[:equal]] = arg[equal+1:]
        else:
            arguments[arg] = True
        
    if 'key' not in arguments:
        raise template.TemplateSyntaxError("gsm_entity requires a key argument (UTSL)")
    
    if 'element' not in arguments:
        if 'tag' not in arguments and 'gsm_id' not in arguments:
            raise template.TemplateSyntaxError("gsm_entity requires either element or both tag and gsm_id arguments (UTSL)")

    return GsmEntityNode(**arguments)

class GsmEntityNode(template.Node):
    def __init__(self, **kwargs):
        """ OMG UGLY VOODOO """
        for k, v in kwargs.items():
            try:
                is_int = str(int(v)) == v
            except:
                is_int = False

            if v[0] == '"' or v[0] == "'":
                setattr(self, k, v[1:-1])
            elif is_int:
                setattr(self, k, v)
            else:
                setattr(self, k, template.Variable(v))

    def render(self, context):
        if hasattr(self, 'element'):
            try:
                element = self.element.resolve(context)
            except template.VariableDoesNotExist:
                return ''

            entity = GsmEntity(
                sport = context['sport'],
                gsm_id = element.attrib['%s_id' % element.tag],
                tag = element.tag
            )
            if hasattr(self, 'name'):
                if hasattr(self.name, 'resolve'):
                    entity.name = self.name.resolve(context)
                else:
                    entity.name = self.name
            entity.element = element
        else:
            # not bloating with layers for now, refactor when required
            if hasattr(self.tag, 'resolve'):
                tag = self.tag.resolve(context)
            else:
                tag = self.tag

            if hasattr(self.gsm_id, 'resolve'):
                gsm_id = self.gsm_id.resolve(context)
            else:
                gsm_id = self.gsm_id

            entity = GsmEntity(
                sport = context['sport'],
                gsm_id = gsm_id,
                tag = tag
            )
            if hasattr(self, 'name'):
                if hasattr(self.name, 'resolve'):
                    entity.name = self.name.resolve(context)
                else:
                    entity.name = self.name
            country_code = getattr(self, 'country_code', None)
            if country_code:
                entity.country_code = country_code.resolve(context)

        if hasattr(self.key, 'resolve'):
            key = self.key.resolve(context)
        else:
            key = self.key

        context[key] = entity

        return ''
