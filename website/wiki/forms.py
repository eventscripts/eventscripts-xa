from django import forms
from bbcode import fields

class WikiForm(forms.Form):
    content     = fields.BBCodeFormField(widget=forms.Textarea)
    categories  = forms.CharField()
