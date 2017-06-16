from django import forms
from django.utils.translation import ugettext_lazy as _
from .mixins import PreventionFormMixin
from .fields import JaqPreventionField

class PreventionForm(PreventionFormMixin, forms.Form):
    source = 1
    
    username = forms.CharField(label=_("Username"), max_length=30)



    

    