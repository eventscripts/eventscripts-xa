from models import Category, Page
from django.core.exceptions import ObjectDoesNotExist
from xa.utils import render_to
from django.contrib.auth.decorators import login_required
from django.utils.simplejson import dumps

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

@login_required
@render_to
def edit_page(request, category_name, name):
<<<<<<< local
    return 'wiki/edit.htm', {'page': Page.objects.get_or_404(name=name, categories__name=category_name)}
=======
    try:
        thispage = Page.objects.get(name=name, categories__name=category_name)
    except ObjectDoesNotExist:
        return create_page(request, category, name)
    return 'wiki/edit.htm', {'page': thispage,
                             'categories': thispage.categories.all(),
                             'available_categories': js_available_categories()}
>>>>>>> other

<<<<<<< local
=======
@login_required    
>>>>>>> other
@render_to
<<<<<<< local
def bbhelp(request):
    return 'bbcode/help.htm', {}
=======
def create_page(request, category_name, name):
    if request.method == 'POST':
        return create_page_save(request, category_name, name)
    else: 
        return create_page_form(request, category_name, name)
    
def create_page_form(requets, category_name, name):
    return 'wiki/edit.htm', {'page': None,
                             'categories': [],
                             'pagename': name,
                             'category_name': category_name,
                             'available_categories': js_available_categories()}
    
    
def create_page_save(request, category_name, name):
    pass>>>>>>> other
