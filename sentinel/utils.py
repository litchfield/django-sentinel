import time
from ipaddr import *
from ipaddr import _IPAddrBase, _BaseNet
from django.core.cache import cache
from settings import *

def total_seconds(td):
    return td.seconds + td.days * 24 * 3600

def address_or_network(ip):
    if isinstance(ip, _IPAddrBase):
        return ip
    try:
        return IPAddress(ip.encode('latin-1'))
    except:
        pass
    try:
        ip = IPNetwork(ip.encode('latin-1'))
        # ensure its within the supported NETRANGE
        assert ip.prefixlen in NETRANGE
        return IPNetwork('%s/%s' % (ip.network, ip.prefixlen))
    except:
        pass

def collapse_networks(ips):
    collapsed = []
    for ip in collapse_address_list(ips):
        if isinstance(ip, IPv4Network) and str(ip)[-3:] == '/32':
            ip = IPv4Address(str(ip)[:-3])
        elif isinstance(ip, IPv6Network) and str(ip)[-4:] == '/128':
            ip = ip[:-4]
        collapsed.append(ip)
    return collapsed

def get_range(ip):
    if isinstance(ip, _BaseNet):
        return int(ip[0]), int(ip[-1])
    try:
        return int(ip), int(ip)
    except:
        return []

def cache_is_alive():
    cache.set(CACHE_PREFIX, 'TEST')
    return cache.get(CACHE_PREFIX) == 'TEST'

