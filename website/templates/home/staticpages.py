from django import template
from xa.home.models import StaticPage

register = template.Library()

@register.inclusion_tag('home/include_static_page.htm', takes_context=True)
def include_static_page(context, page_slug):
    try:
        page = StaticPage.objects.get(slug=page_slug)
        translation = page.get_translation(context['LANGUAGE_CODE'][:2])
        return {
            'page': page,
            'translation': translation,
        }
    except StaticPage.DoesNotExist:
        return {
            'page': {
                'slug': 'notfound',
            }
            'translation': {
                'title': 'Page Not Found',
                'content': '%s not found' % page_slug)
            }
        }
