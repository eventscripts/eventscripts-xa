from django.conf.urls.defaults import *
from xa.api.views import *

urlpatterns = patterns('',
    (r'^version/?$', version),
)
