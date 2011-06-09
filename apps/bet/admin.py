from django.contrib import admin

from models import *

class BetInline(admin.TabularInline):
    raw_id_fields = ('session', 'bettype')
    model = Bet

class TicketAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    inlines = (
        BetInline,
    )

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Bet)
admin.site.register(Event)
