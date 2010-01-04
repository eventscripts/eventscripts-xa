from django.conf.urls.defaults import *
from xa.api.views import *

urlpatterns = patterns('',
    (r'^version/$', version),
    (r'^gauth/(?P<configid>\d+)/$', gauth),
)
