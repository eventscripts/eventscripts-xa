from django import forms
from django.conf import settings
from bbcode import fields

class WikiForm(forms.Form):
    """
    The base form for editing/changing wiki pages.
    """
    content     = fields.BBCodeFormField(widget=forms.Textarea)
    categories  = forms.CharField()
    
class WikiTranslateForm(WikiForm):
    """
    Form to translate wiki pages
    """
    language    = forms.ChoiceField(choices=settings.LANGUAGES)
