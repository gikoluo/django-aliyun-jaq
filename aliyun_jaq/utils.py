import sys
from django.core.cache import caches

def get_cache():
    return getattr(caches, 'jaq', caches['default'])
    
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