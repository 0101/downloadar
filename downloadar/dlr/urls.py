from django.conf.urls.defaults import *


urlpatterns = patterns('dlr.views',
    url(r'^$', 'index'),
    url(r'^get_entries/$', 'get_entries', name='get_entries'),
    url(r'^select/$', 'select', name='select'),
    url(r'^unselect/$', 'unselect', name='unselect'),
    url(r'^entry/(?P<entry_id>\d+)/$', 'entry_detail', name='entry_detail'),
)
