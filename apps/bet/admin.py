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

class BetAdmin(admin.ModelAdmin):
    raw_id_fields = ('session',)
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['myvalue'] = context['adminform'].form.instance
        return super(BetAdmin, self).render_change_form(request, context, add, change, form_url, obj)

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Bet, BetAdmin)
admin.site.register(Event)
