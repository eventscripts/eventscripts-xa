from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'^$', overview, name='overview'),
    url(r'^(?P<name>[a-zA-Z0-9_.-]+)/?$', category, name='category'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/?$', page, name='page'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/edit/?$', edit_page, name='edit'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/create/?$', create_page, name='create'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/history/?$', page_history_overview, name='history-overview'),
    url(r'^(?P<category_name>[a-zA-Z0-9_.-]+)/(?P<name>[a-zA-Z0-9_.-]+)/history/(?P<dt>\d{14})/?$', page_history, name='history'),
)
