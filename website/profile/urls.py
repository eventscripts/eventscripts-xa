"""
Profile URLs
"""
from django.conf.urls.defaults import patterns, url
from views import edit

urlpatterns = patterns('',
    url(r'^$', edit, name='edit'),
)
