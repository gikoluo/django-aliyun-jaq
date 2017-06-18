import socket
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string

from aliyun_jaq import client
from aliyun_jaq.utils import get_remote_ip
from aliyun_jaq.constants import TEST_ACCESS_KEY, TEST_ACCESS_SECRET

from .fields import JaqPreventionField, JaqCaptchaField
from .utils import get_cache

class JaqMixin(object):
    error_messages = {
        'captcha_invalid': _('Incorrect, please try again.'),
        'captcha_error': _('Error verifying input, please try again.'),
    }
    
    @property
    def access_key(self):
        return getattr(settings, 'JAQ_ACCESS_KEY', TEST_ACCESS_KEY)

    @property
    def access_secret(self):
        return getattr(settings, 'JAQ_ACCESS_SECRET', TEST_ACCESS_SECRET)

    @property
    def use_ssl(self):
        return getattr(settings, 'JAQ_USE_SSL', True)

class CaptchaFormMixin(JaqMixin, forms.Form):
    captcha = JaqCaptchaField(scene="login") #login_h5

    def clean_captcha(self):
        cleaned_data = self.cleaned_data['captcha']
        #[None, 
        #'0152JIZgtMjy7iQLwB8JakWbAKppYteeWfo7gTAQxQmAM5e5ybmeC4hgRNyX3lvojNX4sZqifBy4P2Ry5u3EvN2nwESFmQBSI2hWHx6u-fxUrKLqWHP2an1qdzMYpipXgD5BdpnmFvh1A2hKLhicj8OZa8avS4V45v-iLM86kCuE0', 
        #'05a1C7nT4bR5hcbZlAujcdyeMzqY3-uwshPclW-XiktoQeLZPgT3SwQ5f2xCbs5Ru2SVmL1Djs0YXCBHDq5_XDekW4COtC9yt1BCtZv1-ALTFiGp4-RSlo2wwzH2kqN58cdblWU6yCL7ei6vq7ykf6Pqz7LOpIB0V8KMQ4_6464OEbljpHXJzNlw4FYni-a_B6RQuA9P97RjpjHI7s5qZppPuERKVmW6GIxrYwW1IDRWMOcYwgyCM0K4i_gG4aV18ct2Sy40m35HAAgut_HRujz0E9Tc3ftrLHvPFKKbjwaT954vU7RYWakbUzTaCiJKTnOFtoxZDjLKR0WHArk3j-CkYF-RPHU090ku2598klRx8Sbd98x54dLmFkjwtkzbKg8h-fBU6_gVVJ1wNqNNM-qneOVGW5LvPHPIZx8AIEyxA', 
        #'FFFF000000000173EED1:1497756898549:0.9584689777810986', 
        #'login']
        
        key, sessionid, sig, token, scene = cleaned_data  # @UnusedVariable key
        
        try:
            check_captcha = client.captcha(
                self.platform,
                sessionid, 
                sig, 
                token, 
                scene,
                access_key=self.access_key,
                access_secret=self.access_secret,
                remoteip=get_remote_ip(),
                data={},
                use_ssl=self.use_ssl)
            
            eventid = get_random_string(length=32)
            cleaned_data[0] = eventid
            check_captcha_cache = { "EventId": eventid, "Result": check_captcha.data }

            get_cache().set(eventid, check_captcha_cache, 600)

            if check_captcha.is_valid == False:
                raise ValidationError(
                    self.error_messages['captcha_invalid']
                )
                
        except socket.error:  # Catch timeouts, etc
            raise ValidationError(
                self.error_messages['captcha_error']
            )

        if not check_captcha.is_valid:
            raise ValidationError(
                self.error_messages['captcha_invalid']
            )
        return cleaned_data

class PreventionFormMixin(JaqMixin, forms.Form):
    prevetion = JaqPreventionField(scene="login") #login_h5

    def clean_prevetion(self):
        cleaned_data = list(self.cleaned_data['prevetion'])
        key, scene, token = cleaned_data # @UnusedVariable key
        phone = self.data['username']

        extra_data = {'phone': phone }

        try:
            check_captcha = client.prevention(
                self.source,
                scene,
                token,
                access_key=self.access_key,
                access_secret=self.access_secret,
                remoteip=get_remote_ip(),
                data=extra_data,
                use_ssl=self.use_ssl)

            eventid = check_captcha.data['EventId']
            cleaned_data[0] = eventid

            get_cache().set(eventid, check_captcha.data, 600)

            if check_captcha.is_valid == False:
                raise ValidationError(
                    self.error_messages['captcha_invalid']
                )
            

        except socket.error:  # Catch timeouts, etc
            raise ValidationError(
                self.error_messages['captcha_error']
            )

        if not check_captcha.is_valid:
            raise ValidationError(
                self.error_messages['captcha_invalid']
            )
        return cleaned_data