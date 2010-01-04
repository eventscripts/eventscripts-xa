from django.db import models
from bbcode import fields
from xa.utils import BaseManager

bbhelptext = 'You may use BBCode Syntax in this field. For further information read the <a href="/bbcode/">documentation</a>.'


class News(models.Model):
    id          = models.AutoField(primary_key=True)
    author      = models.ForeignKey('auth.User', related_name='news')
    title       = models.CharField(max_length=255)
    content     = fields.BBCodeTextField(help_text=bbhelptext)
    postdate    = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-postdate']
        get_latest_by = 'postdate'
        verbose_name_plural = 'News'
    
    def __unicode__(self):
        return self.title


class Release(models.Model):
    id          = models.AutoField(primary_key=True)
    version     = models.CharField(max_length=20)
    file        = models.FileField(upload_to='releases/')
    info        = fields.BBCodeTextField(help_text=bbhelptext)
    releasedate = models.DateTimeField(auto_now_add=True)
    
    objects = BaseManager()
    
    class Meta:
        ordering = ['-releasedate']
        get_latest_by = 'releasedate'
    
    def __unicode__(self):
        return self.version
