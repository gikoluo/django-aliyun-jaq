import os
import unittest

from . import fields
from django.forms import Form


class TestForm(Form):
    captcha = fields.JaqCaptchaField(attrs={'theme': 'white'})


class TestCase(unittest.TestCase):
    def setUp(self):
        os.environ['JAQ_TESTING'] = 'True'

    def test_envvar_enabled(self):
        form_params = {'jaq_captcha_response_field': 'PASSED'}
        form = TestForm(form_params)
        self.assertTrue(form.is_valid())

    def test_envvar_disabled(self):
        os.environ['JAQ_TESTING'] = 'False'
        form_params = {'jaq_captcha_response_field': 'PASSED'}
        form = TestForm(form_params)
        self.assertFalse(form.is_valid())

    def tearDown(self):
        del os.environ['JAQ_TESTING']
