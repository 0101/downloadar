from django.conf.urls.defaults import *

from dlr.views import Download, Entries, EntryListItem


urlpatterns = patterns('dlr.views',
    url(r'^$', 'index'),
    url(r'^entries/$', Entries.as_view(), name='get_entries'),
    url(r'^entry/(?P<entry_id>\d+)/$', EntryListItem.as_view(), name='get_entry'),
    url(r'^select/$', 'select', name='select'),
    url(r'^unselect/$', 'unselect', name='unselect'),
    url(r'^entry_detail/(?P<entry_id>\d+)/$', 'entry_detail', name='entry_detail'),
    url(r'^download/$', Download.as_view(), name='download'),
)
