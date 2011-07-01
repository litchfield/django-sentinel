from datetime import datetime, timedelta
from django.shortcuts import render
from django.db import IntegrityError
from models import *
from track import *
from flags import *
from utils import *
from settings import *

if not cache_is_alive():
    print "Sentinel thinks the cache is dead, so it didn't bother loading."
    class SentinelMiddleware(object):
        pass
else:
    class SentinelMiddleware(object):
        def process_request(self, request):
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            try:
                if ip:
                    flag = get_flag(ip) 
                    if flag is None or int(flag) == MISS:
                        if not track(ip):
                            return block(GREY, ip, request, update=True)
                        return
                    flag = int(flag)
                    if flag == WHITE:
                        request.whitelisted = True
                        return
                    elif flag in (BLACK, GREY):
                        return block(flag, ip, request)
                    elif flag == BROWN:
                        request.brownlisted = True
                        return
            except ValueError:
                pass
            return render(request, 'sentinel/invalid.html', {'ip':ip}, status=403)

def _greylist(ip, useragent, request):
    """Greylist the given ip/useragent, save to database and update cache,
    Auto blacklist them according to AUTO_BLACK and AUTO_BLACK_EMAIL settings"""
    flag = GREY
    try:
        address = Address.objects.get(ip=ip)
    except Address.DoesNotExist:
        address = Address(ip=ip, count=1)
    if address.flag == BLACK:
        return BLACK
    if address.updated and address.updated < datetime.now() - timedelta(EXPIRE):
        address.count += 1
    if address.count > AUTO_BLACK:
        flag = BLACK
        if AUTO_BLACK_EMAIL:
            request_repr = repr(request)
            network_match = str(ip) != str(address.ip)
            msg = render_to_string('sentinel/blacklisted_email.txt', locals())
            mail_admins('Blacklisted %s' % ip, msg)
    address.flag = flag
    address.useragent = useragent
    try:
        address.save()
    except IntegrityError:
        try:
            a = Address.objects.get(ip=ip)
            if address.updated and address.updated < datetime.now() - timedelta(EXPIRE):
                a.count = address.count + 1
            a.flag = flag
            a.useragent = address.useragent
            a.save()
        except Address.DoesNotExist:
            pass
    cache.set(normalised_flag_key(ip), flag, timeout=EXPIRE if flag == GREY else AGES)
    return flag
    
def block(flag, ip, request, update=False):
    useragent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    if flag == GREY and update:
        flag = _greylist(ip, useragent, request)
    ctx = {'ip':ip, 'useragent': useragent}
    return render(request, 'sentinel/%s.html' % FLAGS_DICT[flag].lower(), ctx, status=403)

if cache_is_alive() and not flags_loaded():
    load_flags()