"""
This is where most of the magic happens
"""
import time
from ipaddr import _BaseNet, _IPAddrBase, IPNetwork, IPAddress
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.mail import mail_admins
from django.db import IntegrityError
from django.template.loader import render_to_string
from models import *
from settings import *

NETWORKS_KEY = '%sN' % CACHE_PREFIX
flag_key = lambda ip: '%sF%s' % (CACHE_PREFIX, ip)
track_key = lambda ip: '%sT%s' % (CACHE_PREFIX, ip)

AGES = 60*60*24*365

def address_or_network(ip):
    if isinstance(ip, _IPAddrBase):
        return ip
    try:
        return IPAddress(ip.encode('latin-1'))
    except:
        pass
    try:
        return IPNetwork(ip.encode('latin-1'))
    except:
        pass
    
def check_networks(ip):
    "Checks the ip against the network rules, return flag if found"
    networks = cache.get(NETWORKS_KEY) or load_networks()
    ip = IPNetwork(ip)
    for net, flag in networks:
        if ip in net:
            return flag

def greylist(ip, useragent, request):
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
    address.save()
    cache.set(flag_key(ip), flag, timeout=EXPIRE if flag == GREY else AGES)
    return flag
    
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
    cache.set(key, log, timeout=AGES)
    if wcount > WINDOW_MAX:
        return False
    return True

def total_seconds(td):
    return td.seconds + td.days * 24 * 3600

def load_flag(ip):
    "On-demand reload of address and return flag"
    try:
        address = Address.objects.get(ip=ip)
        update_cache([ address ])
        return address.flag
    except Address.DoesNotExist:
        return

def load_networks():
    "On-demand reload of networks cache and return networks"
    return update_cache(Address.objects.filter(ip__contains='/'))
    
def update_cache(addresses):
    "Bulk updates cache with given address objects and return networks"
    many = {}
    networks = ['']
    for a in addresses:
        ip = a.ip
        flag = a.flag
        key = flag_key(ip)
        if isinstance(ip, _BaseNet):
            networks.append((ip, flag))
        elif flag == GREY:
            since = total_seconds(datetime.now() - a.updated)
            if since < EXPIRE:
                cache.set(key, flag, EXPIRE - since)
            else:
                cache.delete(key)
        else:
            many[key] = flag
    many[NETWORKS_KEY] = networks
    cache.set_many(many, timeout=AGES)
    return networks

def remove_cache(ips):
    "Removes given ips/networks from cache"
    networks = cache.get(NETWORKS_KEY, [])
    networks = [ (ip, flag) for ip, flag in networks if ip not in ips ]
    cache.set(NETWORKS_KEY, networks, timeout=AGES)
    many = [ flag_key(ip) for ip in ips ]
    cache.delete_many(many)

def remove_addresses(qs):
    "Removes address objects from database and cache"
    remove = []
    for a in qs:
        a.delete()
        remove.append(a.ip)
    if remove:
        remove_cache(remove)
    
def init_cache():
    cutoff = datetime.now() - timedelta(seconds=EXPIRE)
    update_cache(Address.objects.iterator())

init_cache()