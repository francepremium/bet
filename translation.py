from modeltranslation.translator import translator, TranslationOptions

from bookmaker.models import *
from gsm.models import *

class NameTranslation(TranslationOptions):
    fields = ('name',)
translator.register(GsmEntity, NameTranslation)
translator.register(Area, NameTranslation)
translator.register(Championship, NameTranslation)
translator.register(Competition, NameTranslation)
translator.register(Season, NameTranslation)
translator.register(Round, NameTranslation)
translator.register(Session, NameTranslation)
translator.register(BetType, NameTranslation)
translator.register(BetChoice, NameTranslation)
