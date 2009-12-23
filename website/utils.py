from django.core import paginator
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson

from cStringIO import StringIO

def json_dump(data):
    sio = StringIO()
    simplejson.dump(data, sio)
    return sio.getvalue()

def render_to(func):
    def deco(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return response
        tpl, data = response
        return render_to_response(tpl, data, RequestContext(request))
    deco.__name__ = func.__name__
    deco.__doc__ = func.__doc__
    return deco


def response(func):
    def deco(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return response
        data, mimetype = response
        return HttpResponse(data, mimetype=mimetype)
    deco.__name__ = func.__name__
    deco.__doc__ = func.__doc__
    return deco


class AttributeNamespace(object):
    def __setattr__(self, attr, value):
        object.__setattr__(self, attr, value)


class Paginator(list):
    def __init__(self, baseurl, objects, perpage, page, bullets=5):
        # Namespaces
        self.urls = AttributeNamespace()
        self.page = AttributeNamespace()
        if baseurl.endswith('/'):
            self.urls.base = baseurl
        else:
            self.urls.base = baseurl + '/'
        # Django paginator
        pgntr = paginator.Paginator(objects, perpage)
        try:
            pg = pgntr.page(page)
            self.page.this = page
            self.urls.this = self.mkurl(page)
        except (paginator.EmptyPage, paginator.InvalidPage):
            pg = pgntr.page(pgntr.num_pages)
            self.page.this = page
            self.urls.this = self.mkurl(page)
        # Set up some page number attributes
        self.page.total = pgntr.num_pages
        self.page.next = self.page.this + 1
        self.page.prev = self.page.this - 1 
        self.page.is_last = self.page.total == self.page.this
        self.page.is_first = self.page.this == 1
        # Set up some url attributes
        self.urls.last = self.mkurl(self.page.total)
        self.urls.first = self.mkurl(1)
        self.urls.next = self.mkurl(self.page.next)
        self.urls.prev = self.mkurl(self.page.prev)
        # Set up hash for caching
        self.page.hash = '%s::%s::%s::%s' % (baseurl, perpage, page, pgntr.num_pages)
        # Set up object list
        self.object_list = pg.object_list
        # Set up the list
        pagelist = [(self.page.this, self.mkurl(self.page.this), True)]
        diff     = 1
        while len(pagelist) < bullets:
            left, right = self.page.this - diff, self.page.this + diff
            action = False
            if right <= self.page.total:
                pagelist.append((right, self.mkurl(right), False))
                action = True
            if left >= 1:
                pagelist.insert(0, (left, self.mkurl(left), False))
                action = True
            if not action:
                break
            diff += 1
        # Check first/last in range
        if pagelist[0][0] != 1:
            self.page.show_first = True
        else:
            self.page.show_first = False
        if pagelist[-1][0] != self.page.total:
            self.page.show_last = True
        else:
            self.page.show_last = False
        self.page.is_multi_page = self.page.total != 1
        list.__init__(self, pagelist)
        
    def mkurl(self, page):
        return self.urls.base + str(page)