from ipaddr import _IPAddrBase, IPAddress, IPNetwork
from django.core.exceptions import ValidationError
from django import forms
from django.db import models

class IPFieldWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if isinstance(value, _IPAddrBase):
            value = u'%s' % value
        return super(IPFieldWidget, self).render(name, value, attrs)

class IPFormField(forms.CharField):
    def clean(self, value):
        from utils import address_or_network
        value = address_or_network(value)
        if not value:
            raise forms.ValidationError('Invalid IP address/network')
        return value
        
class IPField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "IP address or network in IPv4/IPv6"
    empty_strings_allowed = False
    
    def db_type(self, connection):
        return 'varchar(45)'

    def to_python(self, value):
        if not value:
            return
        from utils import address_or_network
        return address_or_network(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class' : IPFormField,
            'widget': IPFieldWidget,
        }
        defaults.update(kwargs)
        return super(IPField, self).formfield(**defaults)
 
