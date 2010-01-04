from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse
from models import Category, Page
from settings import get
import os
import tarfile
import zipfile
import bz2
import gzip
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
    
def myreverse(name, **kwargs):
    """
    My reverser
    """
    return reverse(name, get('WIKI_URLCON', 'xa.wiki.urls'), kwargs=kwargs)

def rel_walkdir(rootdir):
    file_list = []
    for root, subfolder, files in os.walk(rootdir):
        relroot = os.path.relpath(root, rootdir)
        for file in files:
            file_list.append((os.path.join(relroot,file).lstrip('./'),
                              os.path.join(root, file)))
    return file_list

def render_to_obj(*args, **kwargs):
    """
    Wraps render_to_string into a StringIO
    """
    return StringIO(render_to_string(*args, **kwargs))


def get_gzip_obj():
    """
    Get a file-like object for a gzip compression
    """
    return gzip.GzipFile(fileobj=StringIO())

def get_gzip_content(obj):
    """
    Get the content of a gzip file-like object
    """
    obj.seek(0)
    return obj.read()

def get_plain_obj():
    """
    Get a file-like object for a bz2 or zip compression
    """
    return StringIO()

def get_bz2_content(obj):
    """
    Get the content of a bz2 file-like object
    """
    return bz2.compress(obj.getvalue())

def get_zip_content(obj):
    """
    Get the content of a zip file-like object
    """
    return obj.getvalue()


class Archive(object):
    """
    Archive baseclass
    """
    def __init__(self, fileobj):
        self.fileobj = fileobj
        
    def get(self):
        """
        Get the archive (fileobj)
        """
        return self.fileobj
    
    
class TarArchive(Archive):
    """
    Tar Archive class
    Compression is done in the fileobj passed.
    """
    def __init__(self, fileobj):
        Archive.__init__(self, fileobj)
        self.tar = tarfile.TarFile(fileobj=fileobj)
        
    def add_file(self, fileobj, path):
        """
        Add a file to the archive
        """
        tinfo = tarfile.TarInfo(path)
        self.tar.addfile(tinfo, fileobj)
        
        
class ZipArchive(Archive):
    """
    Zip Archive class
    """
    def __init__(self, fileobj):
        Archive.__init__(self, fileobj)
        self.zfile = zipfile.ZipFile(file=fileobj)
        
    def add_file(self, fileobj, path):
        """
        Add a file to the archive
        """
        self.zfile.writestr(path, fileobj.read())
        
        
FORMATS = {
    'tgz': (TarArchive, get_gzip_obj, get_gzip_content, 'application/x-tar-gz'),
    'tbz2': (TarArchive, get_plain_obj, get_bz2_content, 'application/x-bzip2'),
    'zip': (ZipArchive, get_plain_obj, get_zip_content,
            'application/x-zip-compressed'),
}


def build_download(request, lang, frmt):
    """
    Build a downloadable archive of the wiki for given language in given format.
    """
    archive_class, opener, closer, mimetype = FORMATS[frmt]
    archive = archive_class(opener())
    # Get actual files
    # Add Homepage
    homepage = Page.objects.get(is_home=True)
    context = RequestContext(request, {'page': homepage,
                                       'language': lang,
                                       'is_download': True})
    rendered = render_to_obj('wiki/page.htm', context)
    archive.add_file(rendered, 'index.html')
    # Add all pages
    for page in Page.objects.all():
        context = RequestContext(request, {'page': page,
                                           'language': lang,
                                           'is_download': True})
        rendered = render_to_obj('wiki/page.htm', context)
        path = myreverse('page', path=page.name, lang=lang)
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
        rendered = render_to_obj('wiki/category.htm', context)
        path = myreverse('category', lang=lang, category=category.name)
        archive.add_file(rendered, path)
    # Add media
    for media in ('js', 'ss', 'gfx'):
        rootdir = get('WIKI_%s_PATH' % media.upper())
        prefix = get('WIKI_%S_URL_PREFIX' % media.upper())
        if not rootdir:
            continue
        for relpath, abspath in rel_walkdir(rootdir):
            path = '%s/%s' % (prefix, relpath)
            fobj = open(abspath, 'rb')
            archive.add_file(fobj, path)
            fobj.close()
    return closer(archive), mimetype