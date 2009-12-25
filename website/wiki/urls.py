from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^$', overview, name='overview'),
    url(r'^(?P<name>[a-zA-Z0-9_.-]+)/?$', category, name='category'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/?$', page, name='page'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/edit/?$', edit_page, name='edit'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/create/?$', create_page, name='create'),
)