from bbcode import ArgumentTagNode, register, patterns 
import re
from django.core.urlresolvers import reverse

def get_url(name, **kwargs):
    """
    Wrapper or reverse
    """
    return reverse(name, kwargs=kwargs)

class Page(ArgumentTagNode):
    """
    Creates an internal link to another wiki page.

    Usage:

    [code lang=bbdocs linenos=0][page=pagename]Description[/page]
[page]pagename[/page][/code]
    """
    verbose_name = 'Internal Page Link'
    open_pattern = re.compile(patterns.single_argument % 'page')
    close_pattern = re.compile(patterns.closing % 'page')

    def __init__(self, *args, **kwargs):
        ArgumentTagNode.__init__(self, *args, **kwargs)
        if self.context:
            self.lang = self.context.get('language', 'en')
        else:
            self.lang = 'en'

    def parse(self):
        if self.argument:
            inner = ''
            for node in self.nodes:
                if node.__class__.__name__ == 'AutoDetectURL':
                    inner += node.raw_content
                else:
                    inner += node.parse()
            if self.context.get('wiki_downloadable', None) == 'lorem ipsum':
                url = '%s.html' % self.argument
            else:
                url = get_url('wiki:page', lang=self.lang, path=self.argument)
            return '<a href="%s">%s</a>' % (url, inner)
        else:
            inner = ''
            for node in self.nodes:
                if not node.is_text_node:
                    return self.soft_raise("Page tag cannot have nested tags "
                                           "without an argument.")
                else:
                    inner += node.raw_content
            if self.context.get('wiki_downloadable', None) == 'lorem ipsum':
                url = '%s.html' % inner
            else:
                url = get_url('wiki:page', lang=self.lang, path=inner)
            return '<a href="%s">%s</a>' % (url, inner)


class Category(ArgumentTagNode):
    """
    Creates an internal link to a wiki category.

    Usage:

    [code lang=bbdocs linenos=0][category=categoryname]Description[/category]
[category]categoryname[/category][/code]
    """
    verbose_name = 'Internal Category Link'
    open_pattern = re.compile(patterns.single_argument % 'category')
    close_pattern = re.compile(patterns.closing % 'category')

    def __init__(self, *args, **kwargs):
        ArgumentTagNode.__init__(self, *args, **kwargs)
        if self.context:
            self.lang = self.context.get('language', 'en')
        else:
            self.lang = 'en'

    def parse(self):
        if self.argument:
            inner = ''
            for node in self.nodes:
                if node.__class__.__name__ == 'AutoDetectURL':
                    inner += node.raw_content
                else:
                    inner += node.parse()
            if self.context.get('wiki_downloadable', None) == 'lorem ipsum':
                url = 'Category-%s.html' % self.argument
            else:
                url = get_url('wiki:category', lang=self.lang, category=self.argument)
            return '<a href="%s">%s</a>' % (url, inner)
        else:
            inner = ''
            for node in self.nodes:
                if not node.is_text_node:
                    return self.soft_raise("Category tag cannot have nested "
                                           "tags without an argument.")
                else:
                    inner += node.raw_content
            if self.context.get('wiki_downloadable', None) == 'lorem ipsum':
                url = 'Category-%s.html' % inner
            else:
                url = get_url('wiki:category', lang=self.lang, category=inner)
            return '<a href="%s">%s</a>' % (url, inner)

register(Page)
register(Category)
