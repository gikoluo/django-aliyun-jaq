Django reCAPTCHA
================
**Django reCAPTCHA form field/widget integration app.**

.. image:: https://travis-ci.org/gikoluo/django-aliyun-jaq.svg?branch=develop
    :target: https://travis-ci.org/gikoluo/django-aliyun-jaq

.. contents:: Contents
    :depth: 5

Django reCAPTCHA uses a modified version of the `Python reCAPTCHA client
<http://pypi.python.org/pypi/recaptcha-client>`_ which is included in the
package as ``client.py``.


Requirements
------------

Tested with:

* Python: 2.7, 3.5
* Django: 1.8, 1.9, 1.10, 1.11

Installation
------------

#. 首先要注册一个阿里云账号，进入阿里云控制台后通过菜单找到数据风控，开通验证码服务 <http://tb.cn/sI3Hw6x>.

#. 安装 ``pip install django-aliyun-jaq``.

#. Add ``'aliyun_jaq'`` to your ``INSTALLED_APPS`` setting.

#. Add the keys Aliyun JAQ have given you to your Django production settings (leave development settings blank to use the default test keys) as
   ``JAQ_PUBLIC_KEY`` and ``JAQ_PRIVATE_KEY``. For example:

   .. code-block:: python

       JAQ_PUBLIC_KEY = 'MyRecaptchaKey123'
       JAQ_PRIVATE_KEY = 'MyRecaptchaPrivateKey456'

   These can also be specificied per field by passing the ``public_key`` or
   ``private_key`` parameters to ``JaqField`` - see field usage below.

#. If you would like to use the new No Captcha add the setting
   ``NOCAPTCHA = True``. For example:

   .. code-block:: python

       NOCAPTCHA = True

#. If you require a proxy, add a ``JAQ_PROXY`` setting, for example:

   .. code-block:: python

       JAQ_PROXY = 'http://127.0.0.1:8000'

Usage
-----

Field
~~~~~

The quickest way to add JAQ to a form is to use the included
``JaqField`` field class. A ``Jaq`` widget will be rendered with
the field validating itself without any further action required. For example:

.. code-block:: python

    from django import forms
    from aliyun_jaq.fields import JaqField

    class FormWithCaptcha(forms.Form):
        captcha = JaqField()

To allow for runtime specification of keys you can optionally pass the
``private_key`` or ``public_key`` parameters to the constructor. For example:

.. code-block:: python

    captcha = JaqField(
        public_key='76wtgdfsjhsydt7r5FFGFhgsdfytd656sad75fgh',
        private_key='98dfg6df7g56df6gdfgdfg65JHJH656565GFGFGs',
    )

If specified these parameters will be used instead of your reCAPTCHA project
settings.

The JAQ widget supports several `Javascript options variables
<https://help.aliyun.com/document_detail/47502.html?spm=5176.doc28321.6.565.XK7zah>`_ that
customize the behaviour of the widget, such as ``theme`` and ``lang``. You can
forward these options to the widget by passing an ``attr`` parameter to the
field, containing a dictionary of options. For example:

.. code-block:: python

    captcha = JaqField(attrs={
      'theme' : 'clean',
    })

The client takes the key/value pairs and writes out the ``JaqOptions``
value in JavaScript.



Unit Testing
~~~~~~~~~~~~

Django Aliyun JAQ introduces an environment variable ``JAQ_TESTING`` which
helps facilitate tests. The environment variable should be set to ``"True"``,
and cleared, using the ``setUp()`` and ``tearDown()`` methods in your test
classes.

Setting ``JAQ_TESTING`` to ``True`` causes Django Aliyun JAQ to accept
``"PASSED"`` as the ``jaq_response_field`` value. Note that if you are
using the new No Captcha  (ie. with ``NOCAPTCHA = True`` in your
settings) the response field is called ``g-jaq-response``.

Example:

.. code-block:: python

    import os
    os.environ['JAQ_TESTING'] = 'True'

    form_params = {'jaq_response_field': 'PASSED'} # use 'g-jaq-response' param name if using NOCAPTCHA
    form = RegistrationForm(form_params) # assuming only one ReCaptchaField
    form.is_valid() # True

    os.environ['JAQ_TESTING'] = 'False'
    form.is_valid() # False

Passing any other values will cause Django Aliyun JAQ to continue normal
processing and return a form error.

Check ``tests.py`` for a full example.


AJAX
~~~~~

To make reCAPTCHA work in ajax-loaded forms:

#. Import ``jaq_ajax.js`` on your page (not in the loaded template):

   .. code-block:: html

       <script type="text/javascript" src="//g.alicdn.com/sd/pointman/js/pt.js"></script>
       <script type="text/javascript" src="//g.alicdn.com/sd/ncpc/nc.js?t=1497490527215"></script>

#. Add to your Django settings:

   .. code-block:: python

       CAPTCHA_AJAX = True


Disabling SSL
~~~~~~~~~~~~~

This library used to not use SSL by default, but now it does. You can disable
this if required, but you should think long and hard about it before you do so!

You can disable it by setting ``JAQ_USE_SSL = False`` in your Django
settings, or by passing ``use_ssl=False`` to the constructor of
``JaqField``.


Credits
-------
Inspired Luo Chunhui's blogpost titled `Integrating reCAPTCHA with Django
<http://www.luochunhui.com/tumblelog/26/jul/2009/integrating-recaptcha-with-django>`_


``client.py`` taken from `aliyun
<http://jaqassert.alicdn.com/2AliyunServerSdk/aliyun-python-sdk-jaq-20170503.zip?spm=5176.2020520162.afs.24.L4fiaS&file=aliyun-python-sdk-jaq-20170503.zip>`.
