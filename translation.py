from modeltranslation.translator import translator, TranslationOptions

from gsm.models import *

class AreaTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Area, AreaTranslation)

class ChampionshipTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Championship, ChampionshipTranslation)

class CompetitionTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Competition, CompetitionTranslation)

class SeasonTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Season, SeasonTranslation)

class RoundTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Round, RoundTranslation)

class SessionTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Session, SessionTranslation)

class TeamTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Team, TeamTranslation)
