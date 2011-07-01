import time
from django.core.cache import cache
from settings import *

TIMEOUT = max((WINDOW*60), RATE_MAX)

track_key = lambda ip: '%sT%s' % (CACHE_PREFIX, ip)

def track(ip):
    "Tracks the ip using cache and return true if its OK"
    key = track_key(ip)
    log = cache.get(key, [])
    now = long(time.time())
    wcount = 0
    if log:
        wsince = now - (WINDOW*60*60)
        rsince = now - 60
        rcount = 0
        offset = -1
        while True:
            try:
                t = log[offset]
            except IndexError:
                break
            if t > rsince:
                rcount += 1
                if rcount > RATE_MAX:
                    return False
            if t > wsince:
                wcount += 1
                offset -= 1
            else:
                log.pop()
    log.append((ip, now))
    cache.set(key, log, timeout=TIMEOUT)
    if wcount > WINDOW_MAX:
        return False
    return True
