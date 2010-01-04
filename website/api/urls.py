from django.conf.urls.defaults import patterns
from views import version, gauth

urlpatterns = patterns('',
    (r'^version/$', version),
    (r'^gauth/(?P<configid>\d+)/$', gauth),
)
