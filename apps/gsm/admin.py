from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from models import *

admin.site.register(Sport)

class TourAdmin(TranslationAdmin):
    pass

admin.site.register(Tour, TourAdmin)

class SeasonAdmin(TranslationAdmin):
    pass

admin.site.register(Season, SeasonAdmin)

class CompetitionAdmin(TranslationAdmin):
    pass

admin.site.register(Competition, CompetitionAdmin)

class AreaAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'country_code', 'name')

admin.site.register(Area, AreaAdmin)
