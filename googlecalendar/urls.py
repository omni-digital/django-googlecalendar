from django.conf.urls import patterns, url

import googlecalendar.views as gc_views

urlpatterns = [
    url(r'^(?P<slug>[a-z0-9_-]+)/(?P<event>[a-z0-9_-]+)$', gc_views.googlecalendar_event, name='googlecalendar_event'),
    url(r'^(?P<slug>[a-z0-9_-]+)/$', gc_views.googlecalendar, name='googlecalendar_detail'),
    url(r'^$', gc_views.googlecalendar_list, name='googlecalendar'),
]
