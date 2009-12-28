from django import forms
from django.conf import settings
from bbcode import fields

class WikiForm(forms.Form):
    """
    The base form for editing/translating/changing wiki pages. Think of this as
    the wiki's Swiss Army Form.
    """
    content     = fields.BBCodeFormField(widget=forms.Textarea)
    language    = forms.ChoiceField(choices=settings.LANGUAGES)
    categories  = forms.CharField()