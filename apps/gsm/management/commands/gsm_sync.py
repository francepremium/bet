import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

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
            root = gsm.get_tree(code, 'soccer', 'get_areas').getroot()
            for element in root.getchildren():
                if element.tag == 'area':
                    self.save_area(code, element)

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
            'sport': sport,
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
            'type': element.attrib.get('type', None),
            'soccer_type': element.attrib.get('soccertype', None),
            'format': element.attrib.get('format', None),
            'last_updated': element.attrib['last_updated'],
            'display_order': element.attrib.get('display_order', None),
        })

        unique_stuff = {
            'gsm_id': element.attrib['competition_id'],
            'sport': sport,
        }

        if 'championship' in properties:
            unique_stuff['championship'] = properties.pop('championship')

        competition = self.update_model(
            Competition,
            unique_stuff,
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
            'type': element.attrib.get('type', None) or None,
            'gender': element.attrib.get('gender', None) or None,
            'prize_money': element.attrib.get('prize_money', None) or None,
            'prize_currency': element.attrib.get('prize_currency', None) or None,
            'last_updated': element.attrib.get('last_updated', None) or None,
            'start_date': element.attrib.get('start_date', None) or None,
            'end_date': element.attrib.get('end_date', None) or None,
            'service_level': element.attrib.get('service_level', None) or None,
        })

        season = self.update_model(
            Season,
            {
                'gsm_id': element.attrib['season_id'],
                'competition': properties['competition'],
            },
            properties
        )

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
