from django.contrib import admin

from models import *

class SportAdmin(admin.ModelAdmin):
    pass

class AreaAdmin(admin.ModelAdmin):
    list_display = ('gsm_id', 'country_code', 'name')

admin.site.register(Area, AreaAdmin)
admin.site.register(Sport, SportAdmin)
