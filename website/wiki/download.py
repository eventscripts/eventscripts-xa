from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse
from models import Category, Page
from settings import get
import os
import tarfile
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def rel_walkdir(rootdir):
    file_list = []
    for root, subfolder, files in os.walk(rootdir):
        relroot = root.replace(rootdir, '')
        for file in files:
            file_list.append((os.path.join(relroot,file).lstrip('./'),
                              os.path.join(root, file)))
    return file_list

    
class Tar(object):
    def __init__(self, mode):
        self.fileobj = StringIO()
        self.tar = tarfile.open(fileobj=self.fileobj, mode='w:%s' % mode)
        
    def add_file(self, data, path):
        """
        Add a file to the archive
        """
        tinfo = tarfile.TarInfo(path)
        tinfo.size = len(data)
        self.tar.addfile(tinfo, StringIO(data))
        
    def get_archive(self):
        self.tar.close()
        return self.fileobj.getvalue()
        

class Zip(object):
    """
    Zip Archive class
    """
    def __init__(self):
        self.fileobj = StringIO()
        self.zfile = zipfile.ZipFile(file=self.fileobj, mode='w')
        
    def add_file(self, data, path):
        """
        Add a file to the archive
        """
        self.zfile.writestr(path, data)
        
    def get_archive(self):
        self.zfile.close()
        return self.fileobj.getvalue()
        
        
FORMATS = {
    'tgz': (Tar, ('gz',), 'application/x-tar-gz'),
    'tbz2': (Tar, ('bz2',), 'application/x-bzip2'),
    'zip': (Zip, (), 'application/x-zip-compressed'),
}


def build_download(request, lang, frmt):
    """
    Build a downloadable archive of the wiki for given language in given format.
    """
    archive_class, archive_args, mimetype = FORMATS[frmt]
    archive = archive_class(*archive_args)
    # Get actual files
    # Add Homepage
    homepage = Page.objects.get(is_home=True)
    context = RequestContext(request, {'page': homepage,
                                       'language': lang,
                                       'is_download': True})
    rendered = render_to_string('wiki/page.htm', context)
    archive.add_file(rendered, reverse('wiki:home'))
    # Add all pages
    for page in Page.objects.all():
        context = RequestContext(request, {'page': page,
                                           'language': lang,
                                           'is_download': True})
        rendered = render_to_string('wiki/page.htm', context)
        path = reverse('wiki:page', kwargs={'path':page.name, 'lang':lang})
        archive.add_file(rendered, path)
    # Add category pages
    for category in Category.objects.all():
        pages = []
        for page in category.pages.all().order_by('name'):
            tmp = {}
            tmp['obj'] = page
            tmp['langs'] = filter(lambda x: x[0] != lang,
                                  page.get_available_languages())
            pages.append(tmp)
        context = RequestContext(request, {'language': lang,
                                           'category': category.name,
                                           'pages': pages,
                                           'catobj': category,
                                           'is_download': True})
        rendered = render_to_string('wiki/category.htm', context)
        path = reverse('wiki:category', kwargs={'lang': lang,
                                                'category': category.name})
        archive.add_file(rendered, path)
    # Add media
    for media in ('js', 'ss', 'gfx'):
        rootdir = get('WIKI_%s_PATH' % media.upper())
        prefix = get('WIKI_%s_URL_PREFIX' % media.upper())
        if not rootdir:
            continue
        for relpath, abspath in rel_walkdir(rootdir):
            path = '%s/%s' % (prefix, relpath)
            fobj = open(abspath, 'rb')
            data = fobj.read()
            fobj.close()
            archive.add_file(data, path)
    return archive.get_archive(), mimetype
