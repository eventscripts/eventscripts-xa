from django import forms

class EditForm(forms.Form):
    cfgname     = forms.CharField()
    groups      = forms.CharField()