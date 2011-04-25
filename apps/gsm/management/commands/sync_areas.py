from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from gsm.models import *
import gsm

class Command(BaseCommand):
    args = 'n/a'
    help = 'sync areas from gsm'

    def handle(self, *args, **options):
        root = gsm.get_tree('soccer', 'get_areas').getroot()
        for element in root.getchildren():
            if element.tag == 'area':
                self.save_area(element)
    
    def save_area(self, element, parent=None):
        try:
            area = Area.objects.get(gsm_id = element.attrib['area_id'])
        except Area.DoesNotExist:
            area = Area(
                gsm_id = element.attrib['area_id'],
                gsm_name = element.attrib['name'],
                gsm_country_code = element.attrib['countrycode'],
                parent = parent
            )
            area.save()

        for child in element.getchildren():
            self.save_area(child, area)
