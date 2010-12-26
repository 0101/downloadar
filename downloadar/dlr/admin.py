from django.contrib import admin

from dlr.models import Entry, UserProfile


class EntryAdmin(admin.ModelAdmin):
    list_display = 'title', 'feed', 'fetched',
    list_filter = 'feed',
    search_fields = 'title',


admin.site.register(Entry, EntryAdmin)
admin.site.register(UserProfile)
