from django.contrib import admin

try:
    admin.site.disable_action('delete_selected')
except KeyError:
    pass

from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
admin.site.unregister(FlatPage)

class MyFlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title_fr', 'title_en', 'content_fr', 'content_en', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
admin.site.register(FlatPage, MyFlatPageAdmin)
