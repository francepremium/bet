from haystack.indexes import *
from haystack import site

from models import *

class GsmEntityIndex(SearchIndex):
   text = CharField(document=True, use_template=True)
site.register(GsmEntity, GsmEntityIndex)

class CompetitionIndex(SearchIndex):
   text = CharField(document=True, use_template=True)
site.register(Competition, CompetitionIndex)

class SessionIndex(SearchIndex):
   text = CharField(document=True, use_template=True)
site.register(Session, SessionIndex)
