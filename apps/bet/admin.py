from django.contrib import admin

from models import *

class PronosticInline(admin.TabularInline):
    raw_id_fields = ('session', 'bettype')
    model = Pronostic

class BetAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    inlines = (
        PronosticInline,
    )

admin.site.register(Bet, BetAdmin)
