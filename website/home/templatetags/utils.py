from xa.utils import installed_languages

from django import template

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