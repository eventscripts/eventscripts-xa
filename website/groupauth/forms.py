from django import forms

class EditForm(forms.Form):
    """
    The base groupauth edit form
    """
    cfgname     = forms.CharField()
    groups      = forms.CharField()