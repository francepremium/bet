from modeltranslation.translator import translator, TranslationOptions

from gsm.models import GsmEntity, Area

#class GsmEntityTranslation(TranslationOptions):
   #fields = ('name',)
#translator.register(GsmEntity, GsmEntityTranslation)

class AreaTranslation(TranslationOptions):
   fields = ('name',)
translator.register(Area, AreaTranslation)
