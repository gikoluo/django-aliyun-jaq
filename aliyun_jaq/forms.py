from django import forms
from django.utils.translation import ugettext_lazy as _
from .mixins import PreventionFormMixin, CaptchaFormMixin

class PreventionForm(PreventionFormMixin, forms.Form):
    source = 1 #TODO
    
    username = forms.CharField(label=_("Username"), max_length=30)


class CaptchaForm(CaptchaFormMixin, forms.Form):
    platform = 3 #TODO
    
    
    

    

    