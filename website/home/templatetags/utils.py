from xa.utils import installed_languages

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
        context[self.varname] = render_to_string('paginatation.htm',
            {'page': self.pageobj.resolve(context)})


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