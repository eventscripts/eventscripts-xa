from models import News, Release
from xa.utils import render_to
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.translation import check_for_language

@render_to
def home(request):
    return 'home/home.htm', {'news': News.objects.all()[:5]}

@render_to
def download(request, version=None):
    if version is None:
        release = Release.objects.all().latest()
    else:
        release = Release.objects.get_or_404(version=version)
    return 'home/download.htm', {'release': release}

@render_to
def releases(request):
    return 'home/releases.htm', {'releases': Release.objects.all()}
    
def set_language(request, lang):
    next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    if check_for_language(lang):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME,lang)
    return response
