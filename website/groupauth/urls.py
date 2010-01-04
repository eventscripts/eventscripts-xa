from django.conf.urls.defaults import patterns, url
from views import overview, edit, config, download

urlpatterns = patterns('',
    (r'^$', overview),
    url(r'^new/?$', edit, {'config': None}, name='new'),
    url(r'^edit/(?P<cfgid>\d+)/?$', edit, name='edit'),
    url(r'^(?P<cfgid>\d+)/?$', config, name='config'),
    url(r'^(?P<cfgid>\d+)/download/?$', download, name='download'),
)
