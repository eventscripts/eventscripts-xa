from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from models import Category, Page
from settings import get
import os
import tarfile
import zipfile
from StringIO import StringIO

class MyStringIO(StringIO):
    def close(self):
        pass

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
        self.fileobj = MyStringIO()
        self.tar = tarfile.open(fileobj=self.fileobj, mode='w:%s' % mode)
        
    def add_file(self, data, path):
        """
        Add a file to the archive
        """
        sio = StringIO(data)
        sio.seek(0)
        info = tarfile.TarInfo(name=path)
        info.size = len(sio.buf)
        self.tar.addfile(info, fileobj=sio)
        
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
        info = zipfile.ZipInfo(path)
        info.external_attr = 0777 << 16L
        self.zfile.writestr(info, data)
        
    def get_archive(self):
        self.zfile.close()
        return self.fileobj.getvalue()
        
        
FORMATS = {
    'tgz': (Tar, ('gz',), 'application/x-tar-gz', 'tar.gz'),
    'tbz2': (Tar, ('bz2',), 'application/x-bzip2', 'tar.bz2'),
    'zip': (Zip, (), 'application/x-zip-compressed', 'zip'),
}


def build_download(request, lang, frmt):
    """
    Build a downloadable archive of the wiki for given language in given format.
    """
    archive_class, archive_args, mimetype, filext = FORMATS[frmt]
    archive = archive_class(*archive_args)
    # Get actual files
    # Add Homepage
    homepage = Page.objects.get(is_home=True)
    context = RequestContext(request, {'page': homepage,
                                       'language': lang})
    rendered = render_to_string('wiki/downloadable/page.htm', context)
    archive.add_file(rendered.encode('utf8'), 'index.html')
    # Add all pages
    for page in Page.objects.all():
        context = RequestContext(request, {'page': page,
                                           'language': lang})
        rendered = render_to_string('wiki/downloadable/page.htm', context)
        archive.add_file(rendered.encode('utf8'), '%s.html' % page.name)
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
                                           'catobj': category})
        rendered = render_to_string('wiki/downloadable/category.htm', context)
        archive.add_file(rendered.encode('utf8'), 'Category-%s.html' % category.name)
    # Add media
    for media in ('ss', 'gfx'):
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
    return archive.get_archive(), mimetype, filext
