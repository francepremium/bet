from haystack.indexes import *
from haystack import site

from models import *

class ClanIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
site.register(Clan, ClanIndex)
