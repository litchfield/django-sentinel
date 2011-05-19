from django.db import models
from fields import IPField

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

class Address(models.Model):
    ip = IPField(primary_key=True, verbose_name='IP/Network', help_text='IP address or network (eg 172.1.1.1 or 172.0.0.0/24)')
    flag = models.PositiveSmallIntegerField(choices=FLAGS, db_index=True)
    useragent = models.CharField(max_length=255, blank=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    count = models.PositiveIntegerField(default=0, editable=False, help_text='Total number of greylistings and auto-blacklistings')
    
    class Meta:
        verbose_name_plural = 'addresses'
        ordering = ('flag', 'ip', )
        
    def __unicode__(self):
        return str(self.ip)

