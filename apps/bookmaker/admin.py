from django.contrib import admin

from models import *

class BookmakerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name_fr', 'name_en')
admin.site.register(Bookmaker, BookmakerAdmin)

class BetChoiceInline(admin.TabularInline):
    model = BetChoice

class BetTypeAdmin(admin.ModelAdmin):
    list_filter = ('sport',)
    list_display = ('name', 'sport')
    search_fields = ('name_fr', 'name_en')
    inlines = [
        BetChoiceInline,
    ]
admin.site.register(BetType, BetTypeAdmin)

class BetChoiceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name_fr', 'name_en')
admin.site.register(BetChoice, BetChoiceAdmin)
