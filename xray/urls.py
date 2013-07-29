from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from . import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='xray_dashboard'),
                       url(r'^experiments/$', views.experiments,
                           name='xray_experiments'),
                       url(r'^api/experiments/$',
                           views.experiments_json,
                           name='xray_experiments_json'),
                       url(r'^events/data/$', views.events_data,
                           name='xray_events_data'),
                       url(r'^events/$', views.events, name='xray_events'),
                       )
