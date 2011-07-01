from datetime import datetime, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from fields import IPField
from utils import address_or_network, get_range
from settings import *

MISS = -99
BLACK = 0
WHITE = 1
GREY = 2
BROWN = 3

FLAGS = (
    (BLACK, 'Blacklist'),
    (WHITE, 'Whitelist'),
    (GREY, 'Greylist'),
    (BROWN, 'Brownlist'),
)

FLAGS_DICT = dict(FLAGS)

class AddressManager(models.Manager):
    def matching(self, ip):
        ip_from, ip_to = get_range(ip)
        where = "(ip = %s) OR (%s BETWEEN range_from AND range_to) OR (%s BETWEEN range_from AND range_to) OR (%s <= range_from AND %s >= range_to)"
        params = [str(ip), ip_from, ip_to, ip_from, ip_to]
        return self.get_query_set().extra(where=[where], params=params)
    
class Address(models.Model):
    ip = IPField(unique=True, verbose_name='IP/Network', help_text='IP address or network (eg 172.1.1.1 or 172.0.0.0/24)')
    flag = models.PositiveSmallIntegerField(choices=FLAGS, db_index=True)
    useragent = models.CharField(max_length=255, blank=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    count = models.PositiveIntegerField(default=0, editable=False, help_text='Total number of greylistings and auto-blacklistings')
    is_network = models.BooleanField(default=False, editable=False, db_index=True)
    # These could be used for db-based lookups
    range_from = models.DecimalField(db_index=True, max_digits=39, decimal_places=0, editable=False)
    range_to = models.DecimalField(db_index=True, max_digits=39, decimal_places=0, editable=False)
    objects = AddressManager()
    
    class Meta:
        verbose_name_plural = 'addresses'
        ordering = ('flag', 'ip', )
        
    def __unicode__(self):
        return str(self.ip)
    
    @property
    def expiry(self):
        if self.flag == GREY:
            return (self.updated or datetime.now()) + timedelta(seconds=EXPIRE)

    # @property
    # def is_network(self):
    #     return '/' in str(self.ip) 
    #     
    def clean(self):
        super(Address, self).clean()
        self.ip = address_or_network(self.ip)
        if not self.ip:
            raise ValidationError('Invalid IP. Host or network /%s to /%s permitted.' % NETRANGE)
        
    def save(self, *args, **kwargs):
        if self.ip:
            self.range_from, self.range_to = get_range(self.ip)
            self.is_network = (self.range_to - self.range_from) > 0
        super(Address, self).save(*args, **kwargs)

import signals
