from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

import bbcode
bbcode.autodiscover()

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
    (r'^$', 'xa.home.views.home'),
    #===========================================================================
    # Releases
    #===========================================================================
    url(r'^download/?$', 'xa.home.views.download', name='download-newest'),
    url(r'^download/(?P<version>[^/]+)/?$', 'xa.home.views.download', name='download-old'),
    url(r'^releases/?$', 'xa.home.views.releases', name='release-list'),
    #===========================================================================
    # API
    #===========================================================================
    (r'^api/', include('xa.api.urls', namespace='api')),
    #===========================================================================
    # Wiki
    #===========================================================================
    (r'^docs/', include('xa.wiki.urls', namespace='wiki')),
    # bbcode help
    url(r'^bbcode/', 'bbcode.views.help', {'template_name': 'bbcode/help.htm'} , name='bbhelp'),
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
    # Profile
    #===========================================================================
    (r'profile/', include('xa.profile.urls', namespace='profile')),
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