import time
from ipaddr import *
from django.core.cache import cache
from models import *
from utils import *
from settings import *

def flag_key(ip, prefixlen=None, version=None):
    "sortable key"
    return '%sF_%d_%03d_%s' % (CACHE_PREFIX, version or 4, prefixlen or 0, ip)

def normalised_flag_key(ip):
    ip = str(ip).lower()
    if '/' in ip:
        a = IPNetwork(ip)
        return flag_key(a.network, a.prefixlen, a.version)
    elif ':' in ip:
        return flag_key(ip, version=6)
    else:
        return flag_key(ip)

EXISTENCE_KEY = flag_key(0, 0, 0)

def flags_loaded():
    return cache.get(EXISTENCE_KEY) == MISS
    
def load_flags(addresses=None):
    start = time.time()
    if settings.DEBUG:
        print 'Loading sentinel flags...',
    many = { EXISTENCE_KEY: MISS }
    addresses = addresses or Address.objects.iterator()
    c = 0
    for a in addresses:
        c += 1
        key = normalised_flag_key(a.ip)
        if a.expiry:
            timeout = total_seconds(datetime.now() - a.expiry)
            if timeout > 0:
                cache.set(key, a.flag, timeout)
        else:
            many[key] = a.flag
    cache.set_many(many, timeout=AGES)
    msg = 'loaded %d flags in %dms.' % (c, (time.time() - start) * 1000)
    if settings.DEBUG:
        print msg
    return msg

def delete_flags(addresses):
    keys = []
    for a in addresses:
        #print 'del ', normalised_flag_key(str(a.ip))
        keys.append(normalised_flag_key(str(a.ip)))
    cache.delete_many(keys)
    
def get_flag(ip):
    start = time.time()
    if ip in settings.INTERNAL_IPS:
        return WHITE
    keys = [ EXISTENCE_KEY, flag_key(ip) ]
    for netbits in NETRANGE:
        keys.append(normalised_flag_key('%s/%s' % (ip, netbits)))
    hits = cache.get_many(keys)
    if not hits:
        # cache is gone, reload and try again
        # todo: celery delay() this
        load_flags()
        hits = cache.get_many(keys)
    flag = None
    if hits:
        flag = hits[max(hits.keys())]
    #print ip, flag, '%.5f' % (time.time()-start)
    return flag
