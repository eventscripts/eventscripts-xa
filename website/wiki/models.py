from django.db import models
from django.shortcuts import get_object_or_404
from django.conf import settings
from bbcode import fields

class BaseManager(models.Manager):
    def get_or_404(self, *args, **kwargs):
        return get_object_or_404(self, *args, **kwargs)


class Category(models.Model):
    """
    A wiki category
    """
    id          = models.AutoField(primary_key=True)
    name        = models.SlugField(max_length=50, unique=True)
    # pages FK from wiki.Page
    
    objects = BaseManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
    

class Page(models.Model):
    """
    A wiki page
    """
    id          = models.AutoField(primary_key=True)
    name        = models.SlugField(max_length=255, unique=True)
    categories  = models.ManyToManyField(Category, related_name='pages')
    is_home     = models.BooleanField(default=False)
    # versions FK from wiki.Content
    
    objects = BaseManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    
    def get_content(self, language):
        """
        Get the content for a given language (if possible), otherwise try English
        as fallback language. If that fails, just get any language.
        """
        versions = self.versions.filter(language=language)
        if versions:
            return versions.order_by('-postdate')[0]
        versions = self.versions.filter(language='en')
        if version:
            return versions.order_by('-postdate')[0]
        return self.versions.all().order_by('-postdate')[0]
    
    def add_category(self, category):
        """
        Add a category to this page
        """
        # get_or_create returns a tuple!
        cat,_ = Category.objects.get_or_create(name=category)
        self.categories.add(cat)

    @property
    def category_list(self):
        """
        Return a comma delimited list of category names of this page.
        """
        return ','.join(map(lambda x: x[0], self.categories.all().values_list('name')))
    
    def update_content(self, author, content, language):
        """
        Update the content of this page (add a new version/translation)
        """
        return Content.objects.create(author=author, page=self, content=content,
                                      language=language)

    def get_available_languages(self):
        """
        Get a list of tuples of (unique) languages this page is available in.
        The tuples are: (shortform, verbose name)
        """
        return set(map(lambda x: (x.language, x.get_language_display()),Content.objects.filter(page=self).only('language')))

    
class Content(models.Model):
    """
    Content/Version/Translation of a wiki page.
    This model is used for translating pages (using the language field),
    versioning (using postdate field) and holding content (content field).
    It also associates content to users (author field).
    """
    id          = models.AutoField(primary_key=True)
    author      = models.ForeignKey('auth.User', related_name='wiki_pages')
    page        = models.ForeignKey(Page, related_name='versions')
    content     = fields.BBCodeTextField()
    postdate    = models.DateTimeField(auto_now_add=True)
    language    = models.CharField(max_length=2, choices=settings.LANGUAGES)
    
    objects = BaseManager()

    class Meta:
        ordering = ['-postdate']
        get_latest_by = 'postdate'
        verbose_name_plural = 'Page Content'
    
    def __unicode__(self):
        return '%s (%s)' % (self.page.name, self.postdate)

    def get_next(self, language):
        """
        Get the next content in this content's page history
        """
        nexts = Content.objects.filter(page=self.page,
                                       postdate__gt=self.postdate,
                                       language=language)
        nexts = nexts.order_by('postdate')
        if nexts:
            return nexts[0]
        return None

    def get_prev(self, language):
        """
        Get the previous content in this content's page history
        """
        prevs = Content.objects.filter(page=self.page,
                                       postdate__lt=self.postdate,
                                       language=language)
        prevs = prevs.order_by('-postdate')
        if prevs:
            return prevs[0]
        return None

    def get_dt(self):
        """
        Get the timestamp as used in urls.
        """
        return self.postdate.strftime('%Y%m%d%H%M%S')

    def source(self):
        """
        Get the source as bbcode string.
        """
        return '[code lang=bbdocs linenos=0]%s[/code]' % self.content
