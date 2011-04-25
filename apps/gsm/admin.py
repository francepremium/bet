from django.contrib import admin

from models imoprt *

class SportAdmin(admin.ModelAdmin):
    pass

class AreaAdmin(admin.ModelAdmin):
    list_display = ('gsm_id', 'gsm_country_code', 'gsm_name', 'parent')
    list_filter = ('parent',)

admin.site.register(Area, AreaAdmin)
admin.site.register(Sport, SportAdmin)
