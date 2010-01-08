from models import News, Release
from xa.utils import render_to, Paginator
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.translation import check_for_language

@render_to
def news(request, page):
    """
    Render the homepage with some news items
    """
    thepage = Paginator('/news/', News.objects.all(), 5, int(page), bullets=5)
    return 'home/news.htm', {'page': thepage}

@render_to
def news_item(request, slug):
    """
    Render a single news item
    """
    item = News.objects.get_or_404(slug=slug)
    return 'home/newsitem.htm', {'item': item}

@render_to
def download(request, version=None):
    """
    Render the download inormation page
    """
    if version is None:
        release = Release.objects.all().latest()
    else:
        release = Release.objects.get_or_404(version=version)
    return 'home/download.htm', {'release': release}

@render_to
def releases(request):
    """
    Render a list of all releases
    """
    return 'home/releases.htm', {'releases': Release.objects.all()}
    
def set_language(request, lang):
    """
    Change the language for a user
    """
    next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    if check_for_language(lang):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME,lang)
    return response
