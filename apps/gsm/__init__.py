import time
import sha
import urllib
import os.path
import shutil
from lxml import etree

from django.conf import settings

# Prevent: XMLSyntaxError: Attempt to load network entity
etree.set_default_parser(etree.XMLParser(no_network=False, recover=True))

def get_tree(lang, sport, method, update=False, **parameters):
    LANGUAGE_FAILS = (
        'get_team_statistics',
        'get_squads',
    )
    parameters['lang'] = lang
    
    if sport.__class__.__name__ == 'Sport':
        sport = sport.slug

    if sport != 'tennis' and method in ('get_seasons', 'get_competitions'):
        parameters['authorized'] = 'yes'

    if sport == 'soccer' and method in LANGUAGE_FAILS:
        parameters.pop('lang')

    url = '/%s/%s?%s' % (
        sport,
        method,
        urllib.urlencode(parameters)
    )

    cache_filename = '%s.xml' % sha.sha(url).hexdigest()
    cache_filepath = os.path.join(settings.GSM_CACHE, cache_filename)
    cache_lockname = '%s.lock' % cache_filename
    cache_lockpath = os.path.join(settings.GSM_CACHE, cache_lockname)
    print settings.GSM_URL + url

    # ensure cached version is not too old
    if not update and os.path.exists(cache_filepath):
        last = os.path.getmtime(cache_filepath)
        if time.time()-last > 3600*1:
            update = True

    if update or not os.path.exists(cache_filepath):
        ld = os.open(cache_lockpath, os.O_WRONLY | os.O_EXCL | os.O_CREAT)
        os.close(ld)
        tmp_filename, message = urllib.urlretrieve(settings.GSM_URL + url)
        shutil.copyfile(tmp_filename, cache_filepath)
        os.unlink(cache_lockpath)

    tree = etree.parse(cache_filepath)

    if tree.getroot().tag == 'html':
        # no permissions
        return False

    return tree


class GsmException(Exception):
    """
    Parent exception for all exceptions thrown by this app code.
    """
    pass
