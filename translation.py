from modeltranslation.translator import translator, TranslationOptions

from bookmaker.models import *
from gsm.models import *

class NameTranslation(TranslationOptions):
    fields = ('name', )
class AsciiNameTranslation(TranslationOptions):
    fields = ('name', 'ascii_name')

translator.register(GsmEntity, AsciiNameTranslation)
translator.register(Championship, AsciiNameTranslation)
translator.register(Competition, AsciiNameTranslation)
translator.register(Season, AsciiNameTranslation)
translator.register(Round, AsciiNameTranslation)
translator.register(Session, AsciiNameTranslation)
translator.register(Area, NameTranslation)
translator.register(BetType, NameTranslation)
translator.register(BetChoice, NameTranslation)
