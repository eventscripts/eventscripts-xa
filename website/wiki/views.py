from models import Category, Page, Content
from forms import WikiForm
from xa.utils import render_to

import bbcode

from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

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
def page(request, path, lang):
    """
    Render a wiki page for given path (and if possible given language)
    """
    # Try to get the page
    thispage = Page.objects.filter(name=path, versions__language=lang)
    if not thispage:
        # If it does not exist, send the create form
        return HttpResponseRedirect(reverse('wiki:edit',
                                            kwargs={'path': path,
                                                    'lang': lang}))
    thispage = thispage[0] # we can't use Page.objects.get because of __language.
    return 'wiki/page.htm', {'page': thispage,
                             'language': lang or 'en'}

@render_to
def page_history_overview(request, path, lang):
    """
    Show a list of versions of a wiki page for a given language.
    """
    thispage = Page.objects.filter(name=path, versions__language=lang)
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
    content = Content.objects.get_or_404(postdate=postdate,
                                         page__name=path,
                                         language=lang)
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

def change_page(request, path, lang, oldpage=None):
    """
    Proxy which either calls the form constructor or tries to save the content.
    """
    if request.method == 'POST':
        return change_page_save(request, path, lang, oldpage)
    else:
        return change_page_form(request, path, lang, oldpage)
    
def change_page_form(request, path, lang, oldpage):
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
    form = WikiForm(initial=data)
    return 'wiki/change.htm', {'form': form, 'path': path,
                               'create': bool(data['content']), 'lang': lang}

def change_page_save(request, path, lang, oldpage):
    """
    Try to save changes to a page if the submitted form is valid
    """
    # Construct the form
    form = WikiForm(request.POST)
    # Validity check
    if form.is_valid():
        # Get 'clean' data
        data = form.clean()
        if not oldpage:
            oldpage = Page.objects.create(name=path, is_home=False)
        for category in data['categories'].split(','):
            oldpage.add_category(category)
        # Add new content
        oldpage.update_content(request.user, data['content'], data['language'])
        # Explicit save, is this required?
        oldpage.save()
        # Redirect user to the page they edited.
        return HttpResponseRedirect(reverse('wiki:page',
                                            kwargs={'path': path,
                                                    'lang': data['language']}))
    else:
        # If the form is invalid, we re-send the form page.
        return 'wiki/change.htm', {'form': form, 'path': path, 'lang': lang}
