import time
import sha
import urllib
import os.path
import shutil
from lxml import etree

from django.conf import settings

from gsm.models import *

# Prevent: XMLSyntaxError: Attempt to load network entity
etree.set_default_parser(etree.XMLParser(no_network=False, recover=True))

def get_tree(sport, method, **kwargs):
    kwargs['lang'] = settings.GSM_LANGUAGE
    if isinstance(sport, Sport):
        sport = sport.gsm_name

    url = '/%s/%s?%s' % (
        sport,
        method,
        urllib.urlencode(kwargs)
    )

    cache_filename = '%s.xml' % sha.sha(url).hexdigest()
    cache_filepath = os.path.join(settings.GSM_CACHE, cache_filename)
    cache_lockname = '%s.lock' % cache_filename
    cache_lockpath = os.path.join(settings.GSM_CACHE, cache_lockname)
    tmp_filename, message = urllib.urlretrieve(settings.GSM_URL + url)

    stop = False
    while not stop:
        try:
            os.open(cache_lockpath, os.O_WRONLY | os.O_EXCL | os.O_CREAT)
            shutil.copyfile(tmp_filename, cache_filepath)
            os.unlink(cache_lockpath)
            stop = True
        except OSError as e:
            if e.errno == 17 and e.filename == cache_lockpath:
                time.sleep(0.1)
                continue
            raise e

    tree = etree.parse(cache_filepath)

    return tree
