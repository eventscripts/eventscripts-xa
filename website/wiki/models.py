from django.db import models
from django.shortcuts import get_object_or_404
from bbcode import fields

class BaseManager(models.Manager):
    def get_or_404(self, *args, **kwargs):
        return get_object_or_404(self, *args, **kwargs)


class Category(models.Model):
    id          = models.AutoField(primary_key=True)
    name        = models.SlugField(max_length=50, unique=True)
    
    objects = BaseManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    

class Page(models.Model):
    id          = models.AutoField(primary_key=True)
    name        = models.SlugField(max_length=255, unique=True)
    categories  = models.ManyToManyField(Category, related_name='pages')
    
    objects = BaseManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    
    @property
    def content(self):
        if not hasattr(self, '__content_cache'):
            self.__content_cache = self.versions.all().order_by('-postdate')[0]
        return self.__content_cache

    @property
    def category_list(self):
        return ','.join(map(lambda x: x[0], self.categories.all().values_list('name')))
    
    def update_content(self, author, content):
        return Content.objects.create(author=author, page=self, content=content)
    
    
class Content(models.Model):
    id          = models.AutoField(primary_key=True)
    author      = models.ForeignKey('auth.User', related_name='wiki_pages')
    page        = models.ForeignKey(Page, related_name='versions')
    content     = fields.BBCodeTextField()
    postdate    = models.DateTimeField(auto_now_add=True)
    
    objects = BaseManager()
    
    def __unicode__(self):
        return '%s (%s)' % (self.page.name, self.postdate)

    def get_next(self):
        """
        Get the next content in this content's page history
        """
        nexts = Content.objects.filter(page=self.page,
                                       postdate__gt=self.postdate)
        nexts = nexts.order_by('postdate')
        if nexts:
            return nexts[0]
        return None

    def get_prev(self):
        """
        Get the previous content in this content's page history
        """
        prevs = Content.objects.filter(page=self.page,
                                       postdate__lt=self.postdate)
        prevs = prevs.order_by('-postdate')
        if prevs:
            return prevs[0]
        return None
    
    class Meta:
        ordering = ['-postdate']
        get_latest_by = 'postdate'

    def get_dt(self):
        return self.postdate.strftime('%Y%m%d%H%M%S')

    def source(self):
        return '[code lang=bbdocs linenos=0]%s[/code]' % self.content
