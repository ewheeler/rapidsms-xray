from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from . import views

urlpatterns = patterns('',
                       url(r'^$', views.experiments, name='xray_experiments'),
                       url(r'^api/experiements$',
                           views.experiments_json,
                           name='xray_experiments_json'),
                       )
