import json

from django.conf import settings

from aliyunsdkcore.client import AcsClient
from aliyunsdkjaq.request.v20161123 import (
    OtherPreventionRequest,
    LoginPreventionRequest,
    AfsCheckRequest
)

from ._compat import (
    build_opener, ProxyHandler, urlopen
)

DEFAULT_JAQ_REGION = 'cn-hangzhou'
DEFAULT_JAQ_SERVER = "jaq.aliyuncs.com"  # made ssl agnostic


if getattr(settings, "NOCAPTCHA", False):
    DEFAULT_WIDGET_TEMPLATE = 'aliyun_jaq/widget_nocaptcha.html'
else:
    DEFAULT_WIDGET_TEMPLATE = 'aliyun_jaq/widget.html'
DEFAULT_WIDGET_TEMPLATE_AJAX = 'aliyun_jaq/widget_ajax.html'

API_JAQ_REGION = getattr(settings, "JAQ_REGION",
                         DEFAULT_JAQ_REGION)
API_JAQ_SERVER = getattr(settings, "JAQ_SERVER",
                         DEFAULT_JAQ_SERVER)
API_JAQ_VERSION = "1.0.1"


#API_SSL_SERVER = 
#API_SERVER = getattr(settings, "CAPTCHA_API_SERVER", DEFAULT_API_SERVER)
#VERIFY_SERVER = getattr(settings, "CAPTCHA_VERIFY_SERVER",
#                        DEFAULT_VERIFY_SERVER)

if getattr(settings, "CAPTCHA_AJAX", False):
    WIDGET_TEMPLATE = getattr(settings, "CAPTCHA_WIDGET_TEMPLATE",
                              DEFAULT_WIDGET_TEMPLATE_AJAX)
else:
    WIDGET_TEMPLATE = getattr(settings, "CAPTCHA_WIDGET_TEMPLATE",
                              DEFAULT_WIDGET_TEMPLATE)


RECAPTCHA_SUPPORTED_LANUAGES = ('en', 'nl', 'fr', 'de', 'pt', 'ru', 'es', 'tr')


class JaqResponse(object):
    def __init__(self, is_valid, error_code=None, data={}):
        self.is_valid = is_valid
        self.error_code = error_code
        self.data = data


def request(*args, **kwargs):
    """
    Make a HTTP request with a proxy if configured.
    """
    if getattr(settings, 'JAQ_PROXY', False):
        proxy = ProxyHandler({
            'http': settings.JAQ_PROXY,
            'https': settings.JAQ_PROXY,
        })
        opener = build_opener(proxy)

        return opener.open(*args, **kwargs)
    else:
        return urlopen(*args, **kwargs)


def captcha(platform, 
            sessionid, 
            sig, 
            token, 
            scene,
            access_key,
            access_secret,
            remoteip,
            data,
            use_ssl=False):
    
    clt = AcsClient(access_key, access_secret, API_JAQ_REGION)
    
    if not (sessionid and sig and token and scene and
            len(sessionid) and len(sig) and len(token) and len(scene) ):
        return JaqResponse(
            is_valid=False,
            error_code='incorrect-captcha-sol'
        )

    request = AfsCheckRequest.AfsCheckRequest()
    
    #TODO platform
    # 必填参数：请求来源： 1：Android端； 2：iOS端； 3：PC端及其他
    request.set_Platform(3)
    #必填参数：从前端获取，不可更改
    request.set_Session(sessionid)
    #必填参数：从前端获取，不可更改
    request.set_Sig(sig)
    #必填参数：从前端获取，不可更改
    request.set_Token(token)
    #必填参数：从前端获取，不可更改
    request.set_Scene(scene)
    
    httpresp = clt.do_action_with_exception(request)

    #{"Data":{"FnalDecision":0,"FinalScore":800,"EventId":"b24f8de6-da94-4cfa-82c6-d0239b738463","FinalDesc":"HighValue"},
    #"ErrorMsg":"success","ErrorCode":0}
    
    try:
        jsonresp = json.loads(httpresp.decode('utf-8'))
        data = jsonresp['Data']
        error_code = int(jsonresp['ErrorCode'])
        error_msg = jsonresp['ErrorMsg']
    except:
        data = {}
        error_code = -1
        error_msg = 'Error message'

    return JaqResponse(is_valid=(error_code == 0), error_code=error_code, data=data)


def prevention(source,
           scene,
           token,
           access_key,
           access_secret,
           remoteip,
           data,
           use_ssl=False):
    """
    Submits a reCAPTCHA request for verification. Returns JaqResponse
    for the request

    recaptcha_challenge_field -- The value of recaptcha_challenge_field
    from the form
    recaptcha_response_field -- The value of recaptcha_response_field
    from the form
    private_key -- your reCAPTCHA private key
    remoteip -- the user's ip address
    """

    clt = AcsClient(access_key, access_secret, API_JAQ_REGION)

    if not (scene and token and
            len(scene) and len(token)):
        return JaqResponse(
            is_valid=False,
            error_code='incorrect-captcha-sol'
        )

    # if request.get_location_service_code() is not None:
    #     endpoint = self._location_service.find_product_domain(
    #         self.get_region_id(), request.get_location_service_code())

    if scene.startswith('login'):
        request = LoginPreventionRequest.LoginPreventionRequest()
    else:
        request = OtherPreventionRequest.OtherPreventionRequest()
    #request.set_location_service_code(API_JAQ_SERVER)
    #request.set_region_id(API_JAQ_REGION)

    # 必填参数
    request.set_PhoneNumber(getattr(data, 'phone', None)) #TODO
    #request.set_Email("")
    #request.set_UserId("")
    #request.set_IdType(1)

    request.set_Ip(remoteip)
    request.set_ProtocolVersion(API_JAQ_VERSION)
    # 必填参数：登录来源。1：PC网页；2：移动网页；3：APP;4:其它
    request.set_Source(source)
    # 对应前端页面的afs_token，source来源为1&2&4时，必填;
    request.set_JsToken(token)

    # 对应sdk中获取的wtoken，source来源为3时，必填;
    #request.set_SDKToken("")

    # 选填参数
    # request.set_CurrentUrl("")
    # request.set_Agent("")
    # request.set_Cookie("")
    # request.set_SessionId("")
    # request.set_MacAddress("")
    # request.set_Referer("")
    # request.set_UserName("")
    # request.set_CompanyName("")
    # request.set_Address("")
    # request.set_IDNumber("")
    # request.set_BankCardNumber("")
    # request.set_RegisterIp("")
    # request.set_RegisterDate(1L)
    # request.set_AccountExist(1)
    # request.set_ExtendData("")
    # request.set_LoginType(1)
    # request.set_PasswordCorrect(1)

    httpresp = clt.do_action_with_exception(request)

    #{"Data":{"FnalDecision":0,"FinalScore":800,"EventId":"b24f8de6-da94-4cfa-82c6-d0239b738463","FinalDesc":"HighValue"},
    #"ErrorMsg":"success","ErrorCode":0}
    
    try:
        jsonresp = json.loads(httpresp.decode('utf-8'))
        data = jsonresp['Data']
        error_code = int(jsonresp['ErrorCode'])
        error_msg = jsonresp['ErrorMsg']
    except:
        data = {}
        error_code = -1
        error_msg = 'Error mesage'

    return JaqResponse(is_valid=(error_code == 0), error_code=error_code, data=data)
        
