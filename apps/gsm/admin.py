from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from models import *

admin.site.register(Sport)

class TourAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'sport', 'name')
    list_filter = ('sport', 'last_updated')
    search_fields = ('name_fr', 'name_en')

admin.site.register(Tour, TourAdmin)

class SeasonAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'competition', 'name')
    list_filter = ('last_updated', 'competition__sport',)
    search_fields = ('competition__name_fr', 'competition__name_en', 'name_fr', 'name_en')

admin.site.register(Season, SeasonAdmin)

class CompetitionAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'sport', 'area', 'tour', 'name')
    list_filter = ('sport',)
    search_fields = ('area__name_fr', 'area__name_en', 'tour__name_fr', 'tour__name_en', 'name_fr', 'name_en')

admin.site.register(Competition, CompetitionAdmin)

class AreaAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'country_code', 'parent', 'name')

admin.site.register(Area, AreaAdmin)
