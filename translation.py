from modeltranslation.translator import translator, TranslationOptions

from gsm.models import Championship, Season, Competition, Area

class ChampionshipTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Championship, ChampionshipTranslation)

class SeasonTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Season, SeasonTranslation)

class CompetitionTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Competition, CompetitionTranslation)

class AreaTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Area, AreaTranslation)
