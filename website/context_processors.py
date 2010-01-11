from xa.home.models import StaticPage
from utils import installed_languages

def xa(request):
    pages = []
    for page in StaticPage.objects.filter(in_sidebar=True).select_related():
        pages.append(
            (page.slug, 
            page.get_translation(request.LANGUAGE_CODE[:2]).title)
        )
    return {'sidebar_pages': pages,
            'installed_languages': installed_languages}
