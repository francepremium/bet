from modeltranslation.translator import translator, TranslationOptions

from gsm.models import Sport, Tour, Season, Area

class AreaTranslation(TranslationOptions):
    fields = ('name',)
translator.register(Area, AreaTranslation)
