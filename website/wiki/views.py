from models import Category, Page, Content
from forms import WikiForm, WikiTranslateForm
from download import build_download
from xa.utils import render_to

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page

from datetime import datetime

def home(request, lang):
    """
    The view redirecting users who access /docs/.
    """
    # Get the home page.
    home_page = Page.objects.get_or_404(is_home=True)
    # Redirec the user to the wiki page which is the home page. 
    return HttpResponseRedirect(reverse('wiki:page',
                                        kwargs={'path': home_page.name,
                                                'lang': lang or 'en'}))

@render_to
def category(request, lang, category):
    """
    Display a category overview of all pages in this category.
    """
    # Get the category or raise a 404
    cat = Category.objects.get_or_404(name=category)
    # Let's do the heavy lifiting here
    pages = []
    for page in cat.pages.all().order_by('name'):
        tmp = {}
        tmp['obj'] = page
        tmp['langs'] = filter(lambda x: x[0] != lang,
                              page.get_available_languages())
        pages.append(tmp)
    return 'wiki/category.htm', {'language': lang, 'category': category,
                                 'pages': pages, 'catobj': cat,
                                 'is_download': False}

@render_to
def page(request, path, lang):
    """
    Render a wiki page for given path (and if possible given language)
    """
    # Try to get the page
    thispage = Page.objects.select_related().filter(
        name=path, versions__language=lang
    )
    if not thispage:
        # If it does not exist, send the create form
        return HttpResponseRedirect(reverse('wiki:edit',
                                            kwargs={'path': path,
                                                    'lang': lang}))
    # we can't use Page.objects.get because of __language.
    thispage = thispage[0]
    return 'wiki/page.htm', {'page': thispage,
                             'language': lang,
                             'is_download': False}

@render_to
def page_history_overview(request, path, lang):
    """
    Show a list of versions of a wiki page for a given language.
    """
    thispage = Page.objects.select_related().filter(
        name=path, versions__language=lang
    )
    if not thispage:
        raise Http404
    thispage = thispage[0]
    return 'wiki/history_overview.htm', {'page': thispage,
                                         'language': lang}

@render_to
def page_history(request, path, dt, lang):
    """
    Show the version of a wiki page as it was at 'dt'.
    'dt' is a short timestamp in the format: YYYYMMDDhhmmss
    """
    postdate = datetime.strptime(dt, '%Y%m%d%H%M%S')
    content = Content.objects.get_or_404(
        postdate=postdate, page__name=path, language=lang
    )
    return 'wiki/history.htm', {'content': content,
                                'language': lang}

@render_to
@login_required
def edit_page(request, path, lang):
    """
    Edit an (existing) page.
    Requires user to be authenticated.
    """
    try:
        thispage = Page.objects.get(name=path)
    except ObjectDoesNotExist:
        return change_page(request, path, lang)
    return change_page(request, path, lang, thispage)
    
@render_to
@login_required
def translate(request, path, lang):
    """
    Translate a wiki page from 'lang'.
    """
    thispage = Page.objects.filter(name=path, versions__language=lang)
    if not thispage:
        return change_page(request, path, lang)
    thispage = thispage[0]
    return change_page(request, path, lang, thispage, True)

def change_page(request, path, lang, oldpage=None, dotranslate=False):
    """
    Proxy which either calls the form constructor or tries to save the content.
    """
    if request.method == 'POST':
        return change_page_save(request, path, lang, oldpage, dotranslate)
    else:
        return change_page_form(request, path, lang, oldpage, dotranslate)
    
def change_page_form(request, path, lang, oldpage, dotranslate):
    """
    Send the form to change (edit/create) a page.
    """
    data = {'language': lang,
            'content': ''}
    # If oldpage exists, fill the content into the dictionary.
    if oldpage:
        content = oldpage.get_content(lang, strict=True)
        if content:
            data['content'] = content.content
            data['language'] = content.language
        data['categories'] = oldpage.category_list
    # Construct the form
    if dotranslate:
        form = WikiTranslateForm(initial=data)
    else:
        form = WikiForm(initial=data)
    context = {'form': form, 'path': path,
               'create': bool(data['content']),
               'language': lang,
               'translate': oldpage.get_content(lang) if dotranslate else False}
    return 'wiki/change.htm', context

def change_page_save(request, path, lang, oldpage, dotranslate):
    """
    Try to save changes to a page if the submitted form is valid
    """
    # Construct the form
    if dotranslate:
        form = WikiTranslateForm(request.POST)
    else:
         WikiForm(request.POST)
    # Validity check
    if form.is_valid():
        # Get 'clean' data
        data = form.clean()
        if not oldpage:
            oldpage = Page.objects.create(name=path, is_home=False)
        for category in data['categories'].split(','):
            oldpage.add_category(category)
        # Add new content
        oldpage.update_content(request.user, data['content'],
                               data['language'] if dotranslate else lang)
        # Explicit save, is this required?
        oldpage.save()
        # Redirect user to the page they edited.
        return HttpResponseRedirect(reverse('wiki:page',
            kwargs={'path': path,
                    'lang': data['language'] if dotranslate else lang}))
    else:
        # If the form is invalid, we re-send the form page.
        return 'wiki/change.htm', {'form': form, 'path': path,
            'language': lang, 
            'translate': oldpage.get_content(lang) if dotranslate else False,
            'create': bool(oldpage)}

@render_to
def download_overview(request, lang):
    """
    Tell the user what formats they can have the download in
    """
    return 'wiki/download.htm', {'language': lang}

@cache_page(60 * 60 * 24 * 7) # 1 week
def download(request, lang, frmt):
    """
    Download the whole wiki for a certain language
    """
    archive, mimetype, filext = build_download(request, lang, frmt)
    response = HttpResponse(archive, content_type=mimetype)
    response['Content-Disposition'] = (
        'attachment; filename=xa_documentation.%s' % filext
    )
    return response
