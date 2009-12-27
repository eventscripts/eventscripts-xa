from models import Category, Page, Content
from forms import WikiForm
from xa.utils import render_to

import bbcode

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.simplejson import dumps
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from datetime import datetime


def js_available_categories():
    return dumps(map(lambda x: x[0], Category.objects.all().values_list('name')))

def home(request, lang):
    return HttpResponseRedirect(reverse('wiki:page', kwargs={'path':Page.objects.get_or_404(is_home=True).name, 'lang': lang or 'en'}))

@render_to
def category(request, name):
    return 'wiki/category.htm', {'category': Category.objects.get_or_404(name=name)}

@render_to
def page(request, path, lang):
    try:
        thispage = Page.objects.get(name=path)
    except ObjectDoesNotExist:
        return create_page(path)
    return 'wiki/page.htm', {'page': thispage,
                             'language': lang or 'en'}

@render_to
@login_required
def edit_page(request, path, lang):
    try:
        thispage = Page.objects.get(name=path)
    except ObjectDoesNotExist:
        return create_page(request, path, lang)
    if request.method == 'POST':
        form = WikiForm(request.POST)
        if form.is_valid():
            data = form.clean()
            thispage.update_content(request.user, data['content'])
            categories = map(lambda x: Category.objects.get_or_create(name=x.strip())[0],data['categories'].split(','))
            thispage.categories.add(*categories)
            thispage.save()
            return HttpResponseRedirect(reverse('wiki:page', kwargs={'path': path, 'lang': lang}))
        else:
            return 'wiki/edit.htm', {'form': form,
                                     'page_name': name,
                                     'available_categories': js_available_categories()}
    else:
        form = WikiForm(initial={'content': thispage.content.content,
                                 'categories': thispage.category_list})
        return 'wiki/edit.htm', {'form': form,
                                 'page_name': name,
                                 'available_categories': js_available_categories()}
@render_to
def bbhelp(request):
    return 'bbcode/help.htm', {}

@render_to
@login_required
def create_page(request, category_name, name, lang):
    if request.method == 'POST':
        return create_page_save(request, category_name, name)
    else: 
        return create_page_form(request, category_name, name)
    
def create_page_form(request, category_name, name):
    form = WikiForm(initial={'content': '', 'categories': category_name})
    return 'wiki/edit.htm', {'form': form,
                             'page_name': name,
                             'available_categories': js_available_categories()}
    
    
def create_page_save(request, category_name, name):
    form = WikiForm(request.POST)
    if not form.is_valid():
        return 'wiki/edit.htm', {'form': form,
                                 'page_name': name,
                                 'available_categories': js_available_categories()}
    else:
        data = form.clean()
        categories = map(lambda x: Category.objects.get_or_create(name=x.strip())[0],data['categories'].split(','))
        content = data['content']
        page,_ = Page.objects.get_or_create(name=name)
        page.categories.add(*categories)
        page.update_content(request.user, content)
        return HttpResponseRedirect(reverse('wiki:page', kwargs={'category_name':category_name, 'name':name}))

@render_to
def page_history_overview(request, path, lang):
    thispage = Page.objects.get_or_404(name=path)
    return 'wiki/history_overview.htm', {'page': thispage,
                                         'language': lang}

@render_to
def page_history(request, path, dt, lang):
    postdate = datetime.strptime(dt, '%Y%m%d%H%M%S')
    content = Content.objects.get_or_404(postdate=postdate,
                                         page__name=path)
    return 'wiki/history.htm', {'content': content,
                                'language': lang}
