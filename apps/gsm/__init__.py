import logging
import time
import sha
import urllib
import os.path
import shutil
from lxml import etree

from django.conf import settings
from django.db.models import get_model

# Prevent: XMLSyntaxError: Attempt to load network entity
etree.set_default_parser(etree.XMLParser(no_network=False, recover=True))

logger = logging.getLogger('gsm')

def get_object_from_url(url):
    data = []
    Sport = get_model('gsm', 'sport')
    GsmEntity = get_model('gsm', 'gsmentity')
    sports = Sport.objects.all().values_list('slug', flat=True)
    for part in url.split('/'):
        if part in sports:
            data.append(part)
        elif 1 <= len(data) and len(data) < 3:
            data.append(part)
    return GsmEntity.objects.get(sport__slug=data[0], tag=data[1], gsm_id=data[2])

def parse_element_for(parent, tag):
    # simple recursive findall
    for element in parent.getchildren():
        if element.tag == tag:
            yield element
        else:
            for subelement in parse_element_for(element, tag):
                yield subelement

def get_tree(lang, sport, method, update=False, retry=False, **parameters):
    def get_tree_and_root(filename):
        tree = etree.parse(filename)
        root = tree.getroot()
        return tree, root

    for k, v in parameters.items():
        if v is True:
            parameters[k] = 'yes'
        elif v is False:
            parameters[k] = 'no'

    # fix lang, sometimes fr_FR particularely in console/tests
    lang = lang.split('_')[0]

    LANGUAGE_FAILS = (
        'get_team_statistics',
        'get_squads',
        'get_career',
        'get_matches_live',
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
    cache_exists = os.path.exists(cache_filepath)
    logger.debug('accessing %s' % settings.GSM_URL + url)

    # ensure cached version is not too old
    if not update and cache_exists:
        last = os.path.getmtime(cache_filepath)
        if time.time()-last > 3600*1:
            update = True

    if update or not cache_exists:
        try:
            ld = os.open(cache_lockpath, os.O_WRONLY | os.O_EXCL | os.O_CREAT)
            os.close(ld)
        except:
            waited = 0
            while os.path.exists(cache_lockpath):
                time.sleep(settings.GSM_LOCKFILE_POLLRATE)
                waited += 1
                if waited == settings.GSM_LOCKFILE_MAXPOLLS:
                    # we've waited long enought
                    break
            if os.path.exists(cache_lockpath):
                # delete the lockfile and use cached file
                os.unlink(cache_lockpath)
                tree, root = get_tree_and_root(cache_filepath)
                if root.tag == 'html':
                    raise HtmlInsteadOfXml(settings.GSM_URL + url)
                return tree

        if retry:
            tmp_filepath = False
            trycount = 0
            while not tmp_filepath:
                try:
                    tmp_filepath, message = urllib.urlretrieve(settings.GSM_URL + url)
                except IOError:
                    trycount += 1
                    if trycount > retry:
                        raise
                    time.sleep(3)
        else:
            tmp_filepath, message = urllib.urlretrieve(settings.GSM_URL + url)
        tree, root = get_tree_and_root(tmp_filepath)

        if root is None:
            if cache_exists:
                tree, root = get_tree_and_root(cache_filepath)
            else:
                os.unlink(cache_lockpath)
                raise ServerOverloaded(settings.GSM_URL + url)
        else:
            shutil.copyfile(tmp_filepath, cache_filepath)

        os.unlink(cache_lockpath)
    else:
        tree, root = get_tree_and_root(cache_filepath)

    if root.tag == 'html':
        raise HtmlInsteadOfXml(settings.GSM_URL + url)

    return tree

class GsmException(Exception):
    """
    Parent exception for all exceptions thrown by this app code.
    """
    pass

class CannotFindArea(GsmException):
    pass

class HtmlInsteadOfXml(GsmException):
    pass

class ServerOverloaded(GsmException):
    pass
