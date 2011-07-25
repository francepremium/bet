from modeltranslation.translator import translator, TranslationOptions

from bookmaker.models import *
from gsm.models import *

class NameAsciiTranslation(TranslationOptions):
    fields = ('name', 'name_ascii')
translator.register(GsmEntity, NameAsciiTranslation)
translator.register(Championship, NameAsciiTranslation)
translator.register(Competition, NameAsciiTranslation)
translator.register(Season, NameAsciiTranslation)
translator.register(Round, NameAsciiTranslation)
translator.register(Session, NameAsciiTranslation)

class NameTranslation(TranslationOptions):
    fields = ('name', )
translator.register(Area, NameTranslation)
translator.register(BetType, NameTranslation)
translator.register(BetChoice, NameTranslation)
