import sys
from django.core.cache import caches
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

# `get_cache` function has been deprecated since Django 1.7 in favor of `caches`.
try:
    from django.core.cache import caches

    def get_django_cache(backend, **kwargs):
        return caches[backend]
except ImportError:
    from django.core.cache import get_cache as get_django_cache
    
JAQ_CACHE = getattr(settings, 'JAQ_CACHE', DEFAULT_CACHE_ALIAS)

def get_cache():
    return get_django_cache(JAQ_CACHE)
    
def get_remote_ip():
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