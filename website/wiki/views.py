from models import Category, Page
from xa.utils import render_to

@render_to
def overview(request):
    return 'wiki/overview.htm', {'categories': Category.objects.all()}

@render_to
def category(request, name):
    return 'wiki/category.htm', {'category': Category.objects.get_or_404(name=name)}

@render_to
def page(request, category_name, name):
    return 'wiki/page.htm', {'page': Page.objects.get_or_404(name=name, category__name=category_name)}

@render_to
def edit_page(request, category_name, name):
    return 'wiki/edit.htm', {'page': Page.objects.get_or_404(name=name, category__name=category_name)}