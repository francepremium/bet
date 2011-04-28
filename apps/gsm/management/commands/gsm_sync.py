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
            root = gsm.get_tree(code, 'soccer', 'get_areas').getroot()
            for element in root.getchildren():
                if element.tag == 'area':
                    self.save_area(code, element)
    
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
