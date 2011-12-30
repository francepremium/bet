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

class ApiClient(object):
    LANGUAGE_FAILS = (
        'get_team_statistics',
        'get_squads',
        'get_career',
        'get_matches_live',
    )

    def __init__(self, lang, sport, method, update=False, retry=False, **parameters):
        self.sport = sport
        self.method = method
        self.update = update
        self.retry = retry

        for k, v in parameters.items():
            if v is True:
                parameters[k] = 'yes'
            elif v is False:
                parameters[k] = 'no'

        # fix lang, sometimes fr_FR particularely in console/tests
        self.lang = lang.split('_')[0]

        parameters['lang'] = self.lang
        
        if sport.__class__.__name__ == 'Sport':
            self.sport = self.sport.slug

        if sport != 'tennis' and method in ('get_seasons', 'get_competitions'):
            parameters['authorized'] = 'yes'

        if sport == 'soccer' and method in self.__class__.LANGUAGE_FAILS:
            parameters.pop('lang')
        
        if method == 'get_deleted':
            parameters.pop('lang')

        self.parameters = parameters
    
    @property
    def url(self):
        return '/%s/%s?%s' % (
            self.sport,
            self.method,
            urllib.urlencode(self.parameters)
        )

    @property
    def full_url(self):
        return settings.GSM_URL + self.url

    @property
    def cache_filename(self):
        return '%s.xml' % sha.sha(self.url).hexdigest()

    @property
    def cache_filepath(self):
        return os.path.join(settings.GSM_CACHE, self.cache_filename)

    @property
    def lockname(self):
        return '%s.lock' % self.cache_filename
    
    @property
    def lockpath(self):
        return os.path.join(settings.GSM_CACHE, self.lockname)

    @property
    def cache_exists(self):
        return os.path.exists(self.cache_filepath)

    @property
    def cache_valid(self):
        if not self.cache_exists:
            return False

        last = os.path.getmtime(self.cache_filepath)
        if time.time()-last < 3600:
            if self.root.tag == 'html':
                raise HtmlInsteadOfXml(self.full_url)
            return True

    @property
    def tree(self):
        return etree.parse(self.cache_filepath)
    
    @property
    def root(self):
        return self.tree.getroot()

    def lock(self):
        try:
            ld = os.open(self.lockpath, os.O_WRONLY | os.O_EXCL | os.O_CREAT)
            os.close(ld)
        except:
            waited = 0
            while os.path.exists(self.lockpath):
                time.sleep(settings.GSM_LOCKFILE_POLLRATE)
                if waited == settings.GSM_LOCKFILE_MAXPOLLS:
                    break
                else:
                    waited += 1

            if os.path.exists(self.lockpath):
                os.unlink(self.lockpath)

    def unlock(self):
        os.unlink(self.lockpath)

    def refresh_cache(self):
        tmp_filepath = None

        while not tmp_filepath:
            try:
                tmp_filepath, message = urllib.urlretrieve(self.full_url)
                tree = etree.parse(tmp_filepath)
                root = tree.getroot()
                if not root:
                    os.unlink(tmp_filepath)
                    tmp_filepath = None
                    raise ServerOverloaded(self.full_url)
            except IOError, ServerOverloaded:
                trycount += 1
                if trycount > self.retry:
                    raise
                time.sleep(3)

        shutil.copyfile(tmp_filepath, self.cache_filepath)
        os.unlink(tmp_filepath)

    def __call__(self):
        logger.debug('accessing %s' % self.full_url)

        if self.update or not self.cache_valid:
            self.lock()
            try:
                if self.cache_exists:
                    os.unlink(self.cache_filepath)
                self.refresh_cache()
                if not self.cache_valid:
                    logger.warn('invalid cache %s' % self.cache_filepath)
            finally:
                self.unlock()

        if self.cache_valid:
            return self.tree

def get_tree(lang, sport, method, update=False, retry=False, **parameters):
    api = ApiClient(lang, sport, method, update=False, retry=False, **parameters)
    return api()

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
