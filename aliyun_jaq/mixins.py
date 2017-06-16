import socket
from django import forms
from django.conf import settings

from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

from aliyun_jaq import client
from aliyun_jaq.utils import get_remote_ip
from aliyun_jaq.constants import TEST_APP_KEY, TEST_ACCESS_KEY, TEST_ACCESS_SECRET

from .fields import JaqPreventionField
from .utils import get_cache

class PreventionFormMixin(forms.Form):
    prevetion = JaqPreventionField(scene="login") #login_h5
    #source
    #access_key
    #access_secret
    #use_ssl

    @property
    def access_key(self):
        return getattr(settings, 'JAQ_ACCESS_KEY', TEST_ACCESS_KEY)

    @property
    def access_secret(self):
        return getattr(settings, 'JAQ_ACCESS_SECRET', TEST_ACCESS_SECRET)

    @property
    def use_ssl(self):
        return getattr(settings, 'JAQ_USE_SSL', True)

    def clean_prevetion(self):
        print (self.cleaned_data['prevetion'])
        cleaned_data = list(self.cleaned_data['prevetion'])
        key, scene, token = cleaned_data
        phone = self.data['username']

        extra_data = {'phone': phone }

        try:
            check_captcha = client.submit(
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