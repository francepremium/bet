from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from models import *

admin.site.register(Sport)

class ChampionshipAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'sport', 'name')
    list_filter = ('sport', 'last_updated')
    search_fields = ('name_fr', 'name_en')

admin.site.register(Championship, ChampionshipAdmin)

class SeasonAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'competition', 'name')
    list_filter = ('last_updated', 'competition__sport',)
    search_fields = ('competition__name_fr', 'competition__name_en', 'name_fr', 'name_en')

admin.site.register(Season, SeasonAdmin)

class CompetitionAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'sport', 'area', 'championship', 'name', 'important', 'display_order')
    list_filter = ('sport',)
    search_fields = ('area__name_fr', 'area__name_en', 'championship__name_fr', 'championship__name_en', 'name_fr', 'name_en')
    list_editable = ('important', 'display_order')

admin.site.register(Competition, CompetitionAdmin)

class SessionAdmin(admin.ModelAdmin):
    list_display = ('gsm_id', 'name', 'status', 'winner', 'datetime_utc')
    search_fields = ('session_round__name', 'session_round__season__name', 'session_round__season__competition__name', 'name', 'name_ascii')
    list_filter = ('sport', )
    raw_id_fields = ('oponnent_A', 'oponnent_B', 'winner', 'season', 'session_round')

admin.site.register(Session, SessionAdmin)

class GsmEntityAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'name')
    search_fields = ('name_en', 'name_fr', 'gsm_id')

admin.site.register(GsmEntity, GsmEntityAdmin)

class AreaAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'country_code', 'parent', 'name')
    search_fields = ('name_en', 'name_fr', 'parent__name_fr', 'parent__name_en')

admin.site.register(Area, AreaAdmin)
