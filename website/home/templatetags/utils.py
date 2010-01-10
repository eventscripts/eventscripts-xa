from xa.utils import installed_languages
from xa.home.models import StaticPage

from django import template
from django.template.loader import render_to_string

register = template.Library()

class InstalledLanguagesNode(template.Node):
    """
    Node to set the installed languages context var
    """
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        context[self.varname] = installed_languages
        return ''

@register.tag
def get_installed_languages(parser, token):
    """
    {% get_installed_languages as varname %}
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            "get_installed_languages tag must have 2 arguments!"
        )
    return InstalledLanguagesNode(bits[-1])


class PaginationNode(template.Node):
    def __init__(self, pageobj, varname):
        self.pageobj = template.Variable(pageobj)
        self.varname = varname
        
    def render(self, context):
        context[self.varname] = render_to_string('pagination.htm',
            {'page': self.pageobj.resolve(context)})
        return ''


@register.tag
def paginate(parser, token):
    """
    {% paginate page as pagination %}
    """
    bits = token.split_contents()
    if len(bits) != 4:
        raise template.TemplateSyntaxError(
            "paginate tag must have 3 arguments!"
        )
    return PaginationNode(bits[1], bits[3])


class SidebarPagesNode(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        pages = []
        for page in StaticPage.objects.filter(in_sidebar=True).select_related():
            pages.append(
                (page.slug, 
                page.get_translation(context['LANGUAGE_CODE'][:2]).title)
            )
        context[self.varname] = pages
        return ''


@register.tag
def get_sidebar_pages(parser, token):
    """
    {% get_sidebar_pages as pages %}
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            "get_sidebar_pages tag must have 2 arguments!"
        )
    return SidebarPagesNode(bits[-1])
