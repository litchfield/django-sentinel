from netaddr import glob_to_cidrs, IPGlob
from ipaddr import IPAddress, IPNetwork
from django import forms
from models import *
from flags import *
from utils import *
from settings import NETRANGE

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
            if ip and (not hasattr(ip, 'prefixlen') or ip.prefixlen in NETRANGE):
                ips.append(ip)
            else:
                invalid.append(value)
        if invalid:
            raise forms.ValidationError('Invalid IPs: %s - Enabled: %s' % (', '.join(invalid), ' '.join([ '/%d' % d for d in NETRANGE ])))
        
        ips = collapse_networks(ips)
        
        self._new = []
        self._updated = []
        dups = []
        for ip in ips:
            try:
                address = Address.objects.get(ip=str(ip))
                if int(address.flag) != int(self.flag):
                    dups.append((ip, address.ip, FLAGS_DICT[int(address.flag)]))
                else:
                    self._updated.append(address)
            except Address.DoesNotExist:
                address = Address(ip=ip, flag=self.flag)
                self._new.append(address)
        if dups:
            raise forms.ValidationError('Duplicate IPs: %s' % ', '.join([ '%s (%s %s)' % d for d in dups ]))
        return self.cleaned_data
    
    def save(self):
        addresses = self._updated
        for a in self._new:
            a.save()
            addresses.append(a)
        removed = Address.objects.filter(flag=self.flag).exclude(ip__in=[ a.ip for a in addresses ])
        removed.delete()
