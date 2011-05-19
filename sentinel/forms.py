from netaddr import glob_to_cidrs, IPGlob
from ipaddr import IPAddress, IPNetwork
from django import forms
from models import Address, FLAGS_DICT
from utils import *

class BulkForm(forms.Form):
    bulk = forms.CharField(widget=forms.Textarea, required=False)
    
    def __init__(self, flag, data):
        self.flag = flag
        bulk = '\n'.join(Address.objects.filter(flag=flag).values_list('ip', flat=True))
        super(BulkForm, self).__init__(initial={'bulk':bulk}, data=data or None)
        
    def clean(self):
        ips = []
        invalid = []
        bulk = self.cleaned_data.get('bulk')
        for value in bulk.strip().split('\n'):
            if value == '' or value[0] not in '1234567890':
                continue
            if '*' in value:
                parts = str(value.strip()).split('.')
                for x in range(len(parts), 4):
                    parts.append('*')
                value = '.'.join(parts)
                for ip in glob_to_cidrs(value):
                    ips.append(str(ip))
                continue
            ip = address_or_network(value)
            if ip:
                ips.append(ip)
            else:
                invalid.append(value)
        if invalid:
            raise forms.ValidationError('Invalid IPs: %s' % ', '.join(invalid))
        self._new = []
        self._updated = []
        dups = []
        for ip in ips:
            try:
                address = Address.objects.get(pk=ip)
                if int(address.flag) != int(self.flag):
                    dups.append((ip, FLAGS_DICT[int(address.flag)]))
                else:
                    self._updated.append(address)
            except Address.DoesNotExist:
                address = Address(ip=ip, flag=self.flag)
                self._new.append(address)
        if dups:
            raise forms.ValidationError('Duplicate IPs: %s' % ', '.join([ '%s (%s)' % d for d in dups ]))
        return self.cleaned_data
    
    def save(self):
        addresses = self._updated
        for a in self._new:
            a.save()
            addresses.append(a)
        if addresses:
            update_cache(addresses)
        removed = Address.objects.filter(flag=self.flag).exclude(pk__in=[ a.ip for a in addresses ])
        remove_addresses(removed)
