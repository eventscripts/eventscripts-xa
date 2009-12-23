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
        return self.versions.all().order_by('-postdate')[0]
    
    
class Content(models.Model):
    id          = models.AutoField(primary_key=True)
    page        = models.ForeignKey(Page, related_name='versions')
    content     = fields.BBCodeTextField()
    postdate    = models.DateTimeField(auto_now_add=True)
    
    objects = BaseManager()
    
    def __unicode__(self):
        return '%s (%s)' % (self.page.name, self.postdate)
    
    class Meta:
        ordering = ['-postdate']
        get_latest_by = 'postdate'