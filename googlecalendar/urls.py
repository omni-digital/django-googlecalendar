from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('googlecalendar.views',
    url(r'^(?P<calendar>[a-z0-9_-]+)/(?P<event>[a-z0-9_-]+)$', 'googlecalendar_event', name="googlecalendar_event"),
    url(r'^(?P<calendar>[a-z0-9_-]+)/$', 'googlecalendar', name='googlecalendar_detail'),
    url(r'^$', 'googlecalendar_list', name='googlecalendar'),
)
