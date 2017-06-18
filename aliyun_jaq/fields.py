from django import forms
from django.conf import settings

from ._compat import smart_unicode
from .constants import TEST_APP_KEY
from .widgets import JaqPrevention, JaqCaptcha

#<input type='hidden' id='afs_scene' name='afs_scene'/>
#<input type='hidden' id='afs_token' name='afs_token'/>
class JaqPreventionField(forms.CharField):

    def __init__(self, scene, app_key=None, attrs=None, *args, **kwargs):
        """
        JaqPreventionField can accepts attributes which is a dictionary of
        attributes to be passed to the JaqPrevention widget class. The widget will
        loop over any options added and create the RecaptchaOptions
        JavaScript variables as specified in
        https://code.google.com/apis/recaptcha/docs/customization.html
        """
        if attrs is None:
            attrs = {}

        app_key  = app_key if app_key else \
            getattr(settings, 'JAQ_APP_KEY', TEST_APP_KEY)

        self.widget = JaqPrevention(scene=scene, app_key=app_key, attrs=attrs)
        self.required = True
        super(JaqPreventionField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(JaqPreventionField, self).clean(values[2])
        key = smart_unicode(values[0])
        scene = smart_unicode(values[1])
        token = smart_unicode(values[2])

        if not self.required:
            return

        return ( key, scene, token ) #values[0]



class JaqCaptchaField(forms.CharField):
    def __init__(self, scene, app_key=None, attrs=None, *args, **kwargs):
        """
        ReCaptchaField can accepts attributes which is a dictionary of
        attributes to be passed to the ReCaptcha widget class. The widget will
        loop over any options added and create the RecaptchaOptions
        JavaScript variables as specified in
        https://code.google.com/apis/recaptcha/docs/customization.html
        """
        if attrs is None:
            attrs = {}
        app_key  = app_key if app_key else \
            getattr(settings, 'JAQ_APP_KEY', TEST_APP_KEY)

        self.widget = JaqCaptcha(scene=scene, app_key=app_key, attrs=attrs)
        self.required = True
        super(JaqCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(JaqCaptchaField, self).clean(values[1])
        return values

    
