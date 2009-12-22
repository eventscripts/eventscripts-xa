from django.conf.urls.defaults import *
from xa.groupauth.views import *

urlpatterns = patterns('',
    (r'^$', overview),
    url(r'^new/?$', edit, {'config': None}, name='new'),
    url(r'^edit/(?P<config>\d+)/?$', edit, name='edit'),
    url(r'^(?P<id>\d+)/?$', config, name='config'),
    url(r'^(?P<id>\d+)/download/?$', download, name='download'),
)
