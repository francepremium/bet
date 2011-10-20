import datetime
from optparse import make_option

try:
   import cPickle as pickle
except:
   import pickle

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import gsm
from gsm.sync import *
from gsm.models import *

logger = logging.getLogger('gsm')

class Command(BaseCommand):
    def store_status(self, status):
        contents = pickle.dumps(status)
        file = open(self.status_path, 'w+')
        file.write(contents)
        file.close()

    def get_status(self):
        try:
            with file(self.status_path) as f:
                contents = f.read()
                f.close()
            return pickle.loads(contents)
        except:
            status = {
                'sports': [],
                'toplevel': {},
            }
            for code, language in settings.LANGUAGES:
                status['toplevel'][code] = []
            return status
 
    def handle(self, *args, **options):
        self.status_path = os.path.join(settings.VAR_ROOT, 'gsm_install_status')
        status = self.get_status()

        now = datetime.datetime.now()
        last_updated = minimal_date = now - datetime.timedelta(days=365*5)

        for sport in Sport.objects.all():
            if sport.slug in status['sports']:
                logger.debug('Skipping sport ' + sport.slug)
                continue
            
            for code, language in settings.LANGUAGES:
                sync = Sync(sport, last_updated, minimal_date, logger, 
                    language=code, names_only=code != 'en', quiet=True)

                root = sync.get_tree('get_seasons')

                if not root:
                    logger.error('Did not get tree for get_season')
                    return
                
                for e in root.getchildren():
                    if e.tag == 'method' or sync.skip(e):
                        continue

                    if e.tag not in sync._tag_class_map.keys():
                        continue
                    
                    if e.attrib[e.tag + '_id'] in status['toplevel'][code]:
                        logger.debug('Skipping toplevel %s #%s' %
                            (e.tag, e.attrib[e.tag + '_id']))
                        continue

                    sync.update(e)
                    
                    status['toplevel'][code].append(e.attrib[e.tag + '_id'])
                    self.store_status(status)
            
            status['sports'].append(sport.slug)
            for code, language in settings.LANGUAGES:
                status['toplevel'][code] = []
            self.store_status(status)
