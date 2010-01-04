from xa.utils import installed_languages

from django import template

register = template.Library()

class InstalledLanguagesNode(template.Node):
    def __init__(self, varname):
        self.varname = varname
        
    def render(self, context):
        context[self.varname] = installed_languages
        return ''

@register.tag
def get_installed_languages(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            "get_installed_languages tag must have 2 arguments!"
        )
    return InstalledLanguagesNode(bits[-1])