from django.conf.urls.defaults import *
from views import *

wikipages = patterns('',
    url(r'^$', page, name='page'),
    url(r'^\+edit/?$', edit_page, name='edit'),
    url(r'^\+history/?$', page_history_overview, name='history-overview'),
    url(r'^\+history/(?P<dt>\d{14})/?$', page_history, name='history'),
)

urlpatterns = patterns('',
    url(r'^$', home, {'lang':None}, name='home',),
    url(r'^(?P<lang>[a-z]{2})/?$', home, name='home'),
    (r'^(?P<lang>[a-z]{2})/(?P<path>[a-zA-Z0-9/_:.-]+?)/',
    include(wikipages)),
)
