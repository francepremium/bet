from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from models import *

class SportAdmin(admin.ModelAdmin):
    pass

class AreaAdmin(TranslationAdmin):
    list_display = ('gsm_id', 'country_code', 'name')

admin.site.register(Area, AreaAdmin)
admin.site.register(Sport, SportAdmin)
