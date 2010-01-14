from models import News, Release, StaticPage
from xa.utils import render_to, Paginator
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.translation import check_for_language

from breadcrumbs.base import lib

@render_to
def news(request, page):
    """
    Render the homepage with some news items
    """
    thepage = Paginator('/news/', News.objects.all(), 5, int(page), bullets=5)
    return 'home/news.htm', {'page': thepage}
lib.register(news, lambda path, args, kwargs: None)

@render_to
def news_item(request, slug):
    """
    Render a single news item
    """
    item = News.objects.get_or_404(slug=slug)
    return 'home/newsitem.htm', {'item': item}

def get_news_item_name(path, args, kwargs):
    return News.objects.get(slug=kwargs['slug']).title
lib.register(news_item, get_news_item_name)

@render_to
def static_page(request, slug):
    page = StaticPage.objects.get_or_404(slug=slug)
    translation = page.get_translation(request.LANGUAGE_CODE[:2])
    return 'home/staticpage.htm', {'page': page, 'translation': translation}

def get_static_page_name(path, args, kwargs):
   return ' '.join([bit.capitalize() for bit in kwargs['slug'].split('-')]) 
lib.register(static_page, get_static_page_name)

@render_to
def download(request, slug=None):
    """
    Render the latest version information.
    """
    if slug is None:
        release = Release.objects.all().latest()
    else:
        release = Release.objects.get_or_404(slug=slug)
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
