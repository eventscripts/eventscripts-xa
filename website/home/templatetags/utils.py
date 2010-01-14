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

class IfActiveNode(template.Node):
    path = template.Variable('request.path')
    def __init__(self, var, nodelist_true, nodelist_false):
        self.var = var
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def __repr__(self):
        return "<IfActiveNode>"

    def render(self, context):
        val = self.var.resolve(context, True)
        path = self.path.resolve(context)
        if path.startswith(val):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)
        
@register.tag
def ifactive(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise template.TemplateSyntaxError, "%r takes one arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    var = parser.compile_filter(bits[1])
    return IfActiveNode(var, nodelist_true, nodelist_false)
