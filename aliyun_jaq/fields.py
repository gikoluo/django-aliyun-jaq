import os
import sys


from django import forms
from django.conf import settings
try:
    from django.utils.encoding import smart_unicode
except ImportError:
    from django.utils.encoding import smart_text as smart_unicode

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


from .constants import TEST_APP_KEY, TEST_ACCESS_KEY, TEST_ACCESS_SECRET
from .widgets import JaqPrevention, JaqCaptcha
from .utils import get_remote_ip

#<input type='hidden' id='afs_scene' name='afs_scene'/>
#<input type='hidden' id='afs_token' name='afs_token'/>
class JaqPreventionField(forms.CharField):
    default_error_messages = {
        'captcha_invalid': _('Incorrect, please try again.'),
        'captcha_error': _('Error verifying input, please try again.'),
    }

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

        return ( key, scene , token) #values[0]



class JaqCaptchaField(forms.CharField):
    default_error_messages = {
        'captcha_invalid': _('Incorrect, please try again.'),
        'captcha_error': _('Error verifying input, please try again.'),
    }

    def __init__(self, app_key=None, attrs=None, *args, **kwargs):
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

        self.widget = JaqCaptcha(app_key=app_key, attrs=attrs)
        self.required = True
        super(JaqCaptchaField, self).__init__(*args, **kwargs)

    def get_remote_ip(self):
        f = sys._getframe()
        while f:
            if 'request' in f.f_locals:
                request = f.f_locals['request']
                if request:
                    remote_ip = request.META.get('REMOTE_ADDR', '')
                    forwarded_ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
                    ip = remote_ip if not forwarded_ip else forwarded_ip
                    return ip
            f = f.f_back

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        jaq_captcha_challenge_value = smart_unicode(values[0])
        jaq_captcha_response_value = smart_unicode(values[1])

        # if os.environ.get('JAQ_TESTING', None) == 'True' and \
        #         jaq_captcha_response_value == 'PASSED':
        #     return values[0]

        # if not self.required:
        #     return

        check_captcha = client.submit(
            jaq_captcha_challenge_value,
            jaq_captcha_response_value, private_key=self.private_key,
            remoteip=get_remote_ip(), use_ssl=self.use_ssl)

        print("DEBUG3:",  1111111, check_captcha, check_captcha.is_valid, check_captcha.data)


        # try:
        #     check_captcha = client.submit(
        #         jaq_captcha_challenge_value,
        #         jaq_captcha_response_value, private_key=self.private_key,
        #         remoteip=get_remote_ip(), use_ssl=self.use_ssl)

        #     print("DEBUG3:", check_captcha, check_captcha.is_valid, check_captcha.data)

        # except socket.error:  # Catch timeouts, etc
        #     raise ValidationError(
        #         self.error_messages['captcha_error']
        #     )

        if not check_captcha.is_valid:
            raise ValidationError(
                self.error_messages['captcha_invalid']
            )
        return values[0]
