from django.conf.urls.defaults import patterns, url, include
from xa.home.feeds import (
    NewsFeedRSS, NewsFeedAtom, ReleasesFeedRSS, ReleasesFeedAtom
)

from django.contrib import admin
admin.autodiscover()

import bbcode
bbcode.autodiscover()

newsfeeds = {
    'rss': NewsFeedRSS,
    'atom': NewsFeedAtom,
}
releasesfeeds = {
    'rss': ReleasesFeedRSS,
    'atom': ReleasesFeedAtom,
}

password_patterns = patterns('',
    url(r'^change/$',
        'django.contrib.auth.views.password_change',
       {'template_name': 'password/change/change.htm'},
        name='auth_password_change'),
    url(r'^change/done/?$',
        'django.contrib.auth.views.password_change_done',
       {'template_name': 'password/change/done.htm'},
        name='auth_password_change_done'),
    url(r'^reset/?$',
        'django.contrib.auth.views.password_reset',
       {'template_name': 'password/reset/reset.htm',
        'email_template_name': 'email/passwordresetter.email'},
        name='auth_password_reset'),
    url(r'^reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/?$',
        'django.contrib.auth.views.password_reset_confirm',
       {'template_name': 'password/reset/confirm.htm'},
        name='auth_password_reset_confirm'),
    url(r'^reset/complete/?$',
        'django.contrib.auth.views.password_reset_complete',
       {'template_name': 'password/reset/complete.htm'},
        name='auth_password_reset_complete'),
    url(r'^reset/done/?$',
        'django.contrib.auth.views.password_reset_done',
       {'template_name': 'password/reset/done.htm'},
        name='auth_password_reset_done'),
)

urlpatterns = patterns('',
    #===========================================================================
    # Admin
    #===========================================================================
    (r'^admin/', include(admin.site.urls)),
    #===========================================================================
    # Home
    #===========================================================================
    url(r'^$', 'xa.home.views.news', kwargs={'page': 1}, name='home'),
    url(r'^news/?$', 'xa.home.views.news', kwargs={'page': 1}, name='news'),
    url(r'^news/(?P<page>\d+)/?$', 'xa.home.views.news', name='news'),
    url(r'^news/(?P<slug>[a-zA-Z0-9_-]+)/?$', 'xa.home.views.news_item',
        name='news-item'),
    url(r'^newsfeed/?$',
        'django.contrib.syndication.views.feed',
        kwargs={'feed_dict': newsfeeds, 'url': 'rss'}),
    url(r'^newsfeed/(?P<url>rss|atom)/?$',
        'django.contrib.syndication.views.feed',
        kwargs={'feed_dict': newsfeeds},
        name='news-feed'),
    url(r'^releasesfeed/?$',
        'django.contrib.syndication.views.feed',
        kwargs={'feed_dict': releasesfeeds, 'url': 'rss'}),
    url(r'^releasesfeed/(?P<url>rss|atom)/?$',
        'django.contrib.syndication.views.feed',
        kwargs={'feed_dict': releasesfeeds},
        name='releases-feed'),
    # Set Language
    url(r'language/(?P<lang>[a-zA-Z]{2})/?', 'xa.home.views.set_language',
        name='set_language'),
    #===========================================================================
    # Releases
    #===========================================================================
    url(r'^releases/?$', 'xa.home.views.download', name='download-newest'),
    url(r'^release/(?P<slug>[^/]+)/?$', 'xa.home.views.download',
        name='download-old'),
    url(r'^releases/archive/?$', 'xa.home.views.releases', name='release-list'),
    #===========================================================================
    # Static Pages
    #===========================================================================
    url(r'^static/(?P<slug>[^/]+)/?$', 'xa.home.views.static_page',
        name='static-page'),
    #===========================================================================
    # API
    #===========================================================================
    (r'^api/', include('xa.api.urls', namespace='api')),
    #===========================================================================
    # Wiki
    #===========================================================================
    (r'^docs/', include('xa.wiki.urls', namespace='wiki')),
    # bbcode help
    url(r'^bbcode/', 'bbcode.views.help', {'template_name': 'bbcode/help.htm'},
        name='bbhelp'),
    #===========================================================================
    # Groupauth
    #===========================================================================
    (r'groupauth/', include('xa.groupauth.urls', namespace='gauth')),
    #===========================================================================
    # Login/Logout
    #===========================================================================
    url(r'^login/?$', 'django.contrib.auth.views.login',
        {'template_name':'home/login.htm'}, name='auth_login'),
    url(r'^logout/?$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='auth_logout'),
    #===========================================================================
    # django-registration
    #===========================================================================
    # Registration
    url(r'^register/activate/(?P<activation_key>\w+)/$',
       'registration.views.activate',
       {'template_name': 'register/activate.htm'},
        name='registration_activate'),
    url(r'^register/?$',
        'registration.views.register',
       {'template_name': 'register/register.htm'},
        name='registration_register'),
    url(r'^register/complete/$',
       'django.views.generic.simple.direct_to_template',
        {'template': 'register/complete.htm'},
        name='registration_complete'),
    #===========================================================================
    # Password
    #===========================================================================
    (r'^password/', include(password_patterns)),
)
