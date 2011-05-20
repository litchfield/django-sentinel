from django.shortcuts import render
from models import *
from utils import *
from settings import *

class SentinelMiddleware(object):
    def process_request(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        try:
            if ip:
                flag = cache.get(flag_key(ip)) or check_networks(ip) or load_flag(ip)
                if not flag:
                    if not track(ip):
                        return blocked(GREY, ip, request, update=True)
                    return
                flag = int(flag)
                if flag == WHITE:
                    request.whitelisted = True
                    return
                elif flag in (BLACK, GREY):
                    return blocked(flag, ip, request)
                elif flag == BROWN:
                    request.brownlisted = True
                    return
        except ValueError:
            pass
        return render(request, 'sentinel/invalid.html', {'ip':ip}, status=403)

def blocked(flag, ip, request, update=False):
    useragent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    if flag == GREY and update:
        flag = greylist(ip, useragent, request)
    ctx = {'ip':ip, 'useragent': useragent}
    return render(request, 'sentinel/%s.html' % FLAGS_DICT[flag].lower(), ctx, status=403)
    
init_cache()