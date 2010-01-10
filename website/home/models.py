"""
'General' Models
"""
from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from bbcode import fields
from xa.utils import BaseManager, installed_languages

bbhelptext = _('You may use BBCode Syntax in this field. For further '
               'information read the <a href="/bbcode/">documentation</a>.')


class News(models.Model):
    """
    News post model.
    """
    id          = models.AutoField(primary_key=True)
    author      = models.ForeignKey('auth.User', related_name='news')
    title       = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=64, unique=True)
    content     = fields.BBCodeTextField(help_text=bbhelptext)
    postdate    = models.DateTimeField(auto_now_add=True)
    
    objects = BaseManager()
    
    class Meta:
        """
        Set default ordering and fix plural
        """
        ordering = ['-postdate']
        get_latest_by = 'postdate'
        verbose_name_plural = 'News'
    
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news-item', kwargs={'slug': self.slug})


class Release(models.Model):
    """
    A XA release
    """
    id          = models.AutoField(primary_key=True)
    version     = models.CharField(max_length=20)
    slug        = models.SlugField(max_length=20)
    file        = models.FileField(upload_to='releases/')
    info        = fields.BBCodeTextField(help_text=bbhelptext)
    releasedate = models.DateTimeField(auto_now_add=True)
    
    objects = BaseManager()
    
    class Meta:
        """
        Set default ordering
        """
        ordering = ['-releasedate']
        get_latest_by = 'releasedate'
    
    def __unicode__(self):
        return self.version

    def get_absolute_url(self):
        return reverse('download-old', kwargs={'slug': self.slug})

class StaticPage(models.Model):
    """
    Static information page (eg About)
    """
    id          = models.AutoField(primary_key=True)
    slug        = models.SlugField(max_length=20, unique=True,
        help_text=_("Used for the generation of URLs"))
    order       = models.PositiveSmallIntegerField()
    in_sidebar  = models.BooleanField()

    objects     = BaseManager()

    class Meta:
        ordering = ['-order']
    
    def __unicode__(self):
        return self.slug

    def get_translation(self, lang_code):
        try:
            return self.translations.get(lang_code=lang_code)
        except Translation.DoesNotExist:
            try:
                return self.translations.get(lang_code='en')
            except Translation.DoesNotExist:
                return self.translations.all()[0]


class Translation(models.Model):
    staticpage  = models.ForeignKey(StaticPage, related_name='translations')
    title       = models.CharField(max_length=20)
    content     = fields.BBCodeTextField(help_text=bbhelptext)
    lang_code   = models.CharField(max_length=2,
        choices=[(lang, _(lang)) for lang in installed_languages])

    objects     = BaseManager()

    class Meta:
        unique_together = [('staticpage', 'lang_code'),]

    def __unicode__(self):
        return self.title 
