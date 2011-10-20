import datetime
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

try:
    import cPickle as pickle
except:
    import pickle

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
                'last_updated': None,
            }
            return status

    def handle(self, *args, **options):
        self.status_path = os.path.join(settings.VAR_ROOT, 'gsm_last_updated')
        status = self.get_status()

        now = datetime.datetime.now()
        last_updated = status['last_updated'] or now - datetime.timedelta(days=8)
        minimal_date = now - datetime.timedelta(days=365*5)

        for sport in Sport.objects.all():
            sync = Sync(sport, last_updated, minimal_date, logger, 
                language='en')

            if last_updated < now - datetime.timedelta(hours=24):
                start_date = now - datetime.timedelta(hours=23)
            else:
                start_date = last_updated
            root = sync.get_tree('get_deleted', 
                start_date=datetime_to_string(start_date))
            for child in root.getchildren():
                try:
                    gsm_ids = [x.attrib['source_id'] for x in c.getchildren()]
                    sync._tag_class_map[child.tag].filter(gsm_id__in=gsm_ids,
                        sport=sport).delete()
                except:
                    pass

            if sport.slug == 'soccer':
                root = sync.get_tree('get_matches_live', now_playing='yes')
                for e in gsm.parse_element_for(root, 'match'):
                    sync.update(e)
            
            for code, language in settings.LANGUAGES:
                sync = Sync(sport, last_updated, minimal_date, logger, 
                    language=code, names_only=code != 'en')

                root = sync.get_tree('get_seasons', 
                    last_updated=datetime_to_string(last_updated))

                if not root:
                    logger.error('Did not get tree for get_seasons')
                    return
                
                for e in root.getchildren():
                    if e.tag == 'method' or sync.skip(e):
                        continue

                    if e.tag in sync._tag_class_map.keys():
                        sync.update(e)
        
        status['last_updated'] = now - datetime.timedelta(minutes=1)
        self.store_status(status)
