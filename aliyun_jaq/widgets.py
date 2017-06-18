import django, base64, json
from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from .client import WIDGET_TEMPLATE

#<input type='hidden' id='afs_scene' name='afs_scene'/>
#<input type='hidden' id='afs_token' name='afs_token'/>

#<script data-app="ewogICJjb21tb24iOiB7CiAgICAiYXBwa2V5IjogIkZGRkYwMDAwMDAwMDAxNzNFRUQxIiwKICAgICJ1c2VDdXN0b21Ub2tlbiI6IGZhbHNlLAogICAgInNjZW5lIjogIm1lc3NhZ2VfaDUiLAogICAgImZvcmVpZ24iOiAwCiAgfSwKICAidWFiIjogewogICAgIkV4VGFyZ2V0IjogWwogICAgICAicHdkaWQiCiAgICBdLAogICAgInVzZUN1c3RvbVRva2VuIjogZmFsc2UsCiAgICAiRm9ybUlkIjogIm15X2Zvcm0iLAogICAgIkxvZ1ZhbCI6ICJ1YV9sb2ciLAogICAgIlNlbmRJbnRlcnZhbCI6IDIwLAogICAgIlNlbmRNZXRob2QiOiAzLAogICAgIk1heE1DTG9nIjogMTUwLAogICAgIk1heEtTTG9nIjogMTUwLAogICAgIk1heE1QTG9nIjogMTUwLAogICAgIk1heEdQTG9nIjogNSwKICAgICJNYXhUQ0xvZyI6IDE1MCwKICAgICJHUEludGVydmFsIjogNTAsCiAgICAiTVBJbnRlcnZhbCI6IDUwLAogICAgIk1heEZvY3VzTG9nIjogMTUwLAogICAgImlzU2VuZEVycm9yIjogMSwKICAgICJJbWdVcmwiOiAiLy9jZmQuYWxpeXVuLmNvbS9jb2xsZWN0b3IvYW5hbHl6ZS5qc29ucCIsCiAgICAiR2V0QXR0cnMiOiBbCiAgICAgICJocmVmIiwKICAgICAgInNyYyIKICAgIF0sCiAgICAiRmxhZyI6IDE5NjU1NjcKICB9LAogICJ1bWlkIjogewogICAgInRpbWVvdXQiOiAzMDAwLAogICAgInRpbWVzdGFtcCI6ICIiLAogICAgInRva2VuIjogIiIsCiAgICAic2VydmljZVVybCI6ICJodHRwczovL3ludWYuYWxpcGF5LmNvbS9zZXJ2aWNlL3VtLmpzb24iLAogICAgImFwcE5hbWUiOiAiIiwKICAgICJjb250YWluZXJzIjogewogICAgICAiZmxhc2giOiAiY29udGFpbmVyIiwKICAgICAgImRjcCI6ICJjb250YWluZXIiCiAgICB9CiAgfQp9"
#            src="//g.alicdn.com/sd/pointman/js/pt.js"></script>

class JaqPrevention(forms.widgets.Widget):
    input_type = 'hidden'
    
    if getattr(settings, 'NOCAPTCHA', False):
        jaq_prevention_key_name = 'g-jaq-prevention-key'
        jaq_prevention_scene_name = 'g-jaq-prevention-scene'
        jaq_prevention_token_name = 'g-jaq-prevention-token'
    else:
        jaq_prevention_key_name = 'jaq_prevention_key_field'
        jaq_prevention_scene_name = 'jaq_prevention_scene_field'
        jaq_prevention_token_name = 'jaq_prevention_token_field'

    template_name = 'aliyun_jaq/widget_prevention.html'

    def __init__(self, scene, app_key, *args, **kwargs):
        super(JaqPrevention, self).__init__(*args, **kwargs)
        self.key = None
        self.scene = scene
        self.app_key = app_key

    def value_from_datadict(self, data, files, name):
        return [
            data.get(self.jaq_prevention_key_name, None),
            data.get(self.jaq_prevention_scene_name, None),
            data.get(self.jaq_prevention_token_name, None),
        ]

    def get_data_app(self):
        return {
          "common": {
            "appkey": self.app_key,
            "useCustomToken": False,
            "scene": self.scene,
            "foreign": 0
          },
          "uab": {
            "ExTarget": [
              "pwdid"
            ],
            "useCustomToken": False,
            "FormId": "my_form",
            "LogVal": "ua_log",
            "SendInterval": 20,
            "SendMethod": 3,
            "MaxMCLog": 150,
            "MaxKSLog": 150,
            "MaxMPLog": 150,
            "MaxGPLog": 5,
            "MaxTCLog": 150,
            "GPInterval": 50,
            "MPInterval": 50,
            "MaxFocusLog": 150,
            "isSendError": 1,
            "ImgUrl": "//cfd.aliyun.com/collector/analyze.jsonp",
            "GetAttrs": [
              "href",
              "src"
            ],
            "Flag": 1965567
          },
          "umid": {
            "timeout": 3000,
            "timestamp": "",
            "token": "",
            "serviceUrl": "https://ynuf.alipay.com/service/um.json",
            "appName": "",
            "containers": {
              "flash": "container",
              "dcp": "container"
            }
          }
        }

    def render(self, name, value, attrs=None, renderer=None):
        if django.VERSION < (1, 11):
            return mark_safe(render_to_string(
                self.template_name,
                self.get_context(name, value, attrs)
            ))
        else:
            return super(JaqPrevention, self).render(
                name, value, attrs=attrs, renderer=renderer
            )

    def get_context(self, name, value, attrs):

        try:
            lang = attrs['lang']
        except KeyError:
            # Get the generic language code
            lang = get_language().split('-')[0]

        try:
            context = super(JaqPrevention, self).get_context(name, value, attrs)
        except AttributeError:
            context = {}
        context.update({
            #'api_server': API_SERVER,
            'app_key': self.app_key,
            'app_data': base64.b64encode( json.dumps(self.get_data_app() ).encode('UTF-8') ), 
            'scene': self.scene,
            'lang': lang,
            'options': mark_safe(json.dumps(self.attrs, indent=2)),
        })
        return context

    
# <input type='hidden' id='csessionid' name='csessionid'/>
# <input type='hidden' id='sig' name='sig'/>
# <input type='hidden' id='token' name='token'/>
# <input type='hidden' id='scene' name='scene'/>
class JaqCaptcha(forms.widgets.Widget):
    input_type = 'hidden'
    
    if getattr(settings, 'NOCAPTCHA', False):
        jaq_captcha_key_name = 'g-jaq-captcha-key'
        jaq_captcha_session_name = 'g-jaq-captcha-session'
        jaq_captcha_sig_name = 'g-jaq-captcha-sig'
        jaq_captcha_token_name = 'g-jaq-captcha-token'
        jaq_captcha_scene_name = 'g-jaq-captcha-scene'
    else:
        jaq_captcha_key_name = 'jaq_captcha_key_field'
        jaq_captcha_session_name = 'jaq_captcha_session_field'
        jaq_captcha_sig_name = 'jaq_captcha_sig_field'
        jaq_captcha_token_name = 'jaq_captcha_token_field'
        jaq_captcha_scene_name = 'jaq_captcha_scene_field'

    template_name = WIDGET_TEMPLATE

    def __init__(self, scene, app_key, *args, **kwargs):
        super(JaqCaptcha, self).__init__(*args, **kwargs)
        self.key = None
        self.scene = scene
        self.app_key = app_key

    def value_from_datadict(self, data, files, name):
        return [
            data.get(self.jaq_captcha_key_name, None),
            data.get(self.jaq_captcha_session_name, None),
            data.get(self.jaq_captcha_sig_name, None),
            data.get(self.jaq_captcha_token_name, None),
            data.get(self.jaq_captcha_scene_name, None)
        ]

    def render(self, name, value, attrs=None, renderer=None):
        if django.VERSION < (1, 11):
            return mark_safe(render_to_string(
                self.template_name,
                self.get_context(name, value, attrs)
            ))
        else:
            return super(JaqCaptcha, self).render(
                name, value, attrs=attrs, renderer=renderer
            )

    def get_context(self, name, value, attrs):
        try:
            lang = attrs['lang']
        except KeyError:
            # Get the generic language code
            lang = get_language().split('-')[0]

        try:
            context = super(JaqCaptcha, self).get_context(name, value, attrs)
        except AttributeError:
            context = {}

        context.update({
            'app_key': self.app_key,
            'scene': self.scene,
            'lang': lang,
            'options': mark_safe(json.dumps(self.attrs, indent=2)),
        })

        return context
