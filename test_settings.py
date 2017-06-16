DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite',
    }
}

INSTALLED_APPS = [
    'aliyun_jaq',
]

RECAPTCHA_PRIVATE_KEY = 'privkey'
RECAPTCHA_PUBLIC_KEY = 'pubkey'
