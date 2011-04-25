from modeltranslation.translator import translator, TranslationOptions

from gsm.models import Tour, Season, Competition, Area

class TourTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Tour, TourTranslation)

class SeasonTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Season, SeasonTranslation)

class CompetitionTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Competition, CompetitionTranslation)

class AreaTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Area, AreaTranslation)
