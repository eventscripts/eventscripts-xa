from models import Category, Page
from forms import WikiForm
from xa.utils import render_to

import bbcode

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.simplejson import dumps
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse


def js_available_categories():
    return dumps(map(lambda x: x[0], Category.objects.all().values_list('name')))

@render_to
def overview(request):
    return 'wiki/overview.htm', {'categories': Category.objects.all()}

@render_to
def category(request, name):
    return 'wiki/category.htm', {'category': Category.objects.get_or_404(name=name)}

@render_to
def page(request, category_name, name):
    try:
        thispage = Page.objects.get(name=name, categories__name=category_name)
    except ObjectDoesNotExist:
        return create_page(category_name, name)
    return 'wiki/page.htm', {'page': thispage}

@render_to
@login_required
def edit_page(request, category_name, name):
    try:
        thispage = Page.objects.get(name=name, categories__name=category_name)
    except ObjectDoesNotExist:
        return create_page(request, category_name, name)
    if request.method == 'POST':
        form = WikiForm(request.POST)
        if form.is_valid():
            data = form.clean()
            thispage.update_content(request.user, data['content'])
            categories = map(lambda x: Category.objects.get_or_create(name=x.strip())[0],data['categories'].split(','))
            thispage.categories.add(*categories)
            thispage.save()
            return HttpResponseRedirect(reverse('wiki:page', kwargs={'name': name, 'category_name': category_name}))
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
def create_page(request, category_name, name):
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
