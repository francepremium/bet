from haystack.indexes import *
from haystack import site

from models import *

class BookmakerIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
site.register(Bookmaker, BookmakerIndex)
