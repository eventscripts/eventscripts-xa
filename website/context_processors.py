from xa.home.models import StaticPage
from xa.wiki.models import Page
from utils import installed_languages

def xa(request):
    pages = []
    for page in StaticPage.objects.filter(in_sidebar=True).select_related():
        pages.append(
            (page.slug, 
            page.get_translation(request.LANGUAGE_CODE[:2]).title)
        )
    guides = []
    for guide in Page.objects.filter(in_sidebar=True):
        guides.append(guide.name)
    return {'sidebar_pages': pages,
            'sidebar_guides': guides,
            'installed_languages': installed_languages,
            'active_page': request.path.strip('/').split('/')[0],
            'language': request.LANGUAGE_CODE[:2]}
