from django import template

register = template.Library()

@register.filter
def get_content(page, language):
    return page.content(language)

@register.filter
def get_versions(page, language):
    return page.versions.filter(language=language)

@register.filter
def get_next(content, language):
    return content.get_next(language)

@register.filter
def get_prev(content, language):
    return content.get_prev(language)
