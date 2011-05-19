from django.conf.urls.defaults import patterns
from django.contrib.messages import success
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from models import *
from utils import update_cache, remove_cache
from forms import BulkForm

class AddressAdmin(admin.ModelAdmin):
    list_display = ('ip_', 'flag', 'useragent_', 'updated')
    list_filter = ('flag', 'updated', )
    search_fields = ('ip', )
    readonly_fields = ('useragent', 'count', 'created', 'updated', )
    actions = None
    
    def save_model(self, request, obj, form, change):
        obj.save()
        update_cache([obj])

    def delete_model(self, request, obj):
        remove_cache([obj.ip])
        obj.delete()
    
    def get_urls(self):
        urls = super(AddressAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^bulk/(\d)/$', admin_bulk),
        )
        return my_urls + urls
    
    def useragent_(self, obj):
        TRIM = 50
        if len(obj.useragent) > TRIM:
            return '%s...'%obj.useragent[:TRIM]
        return obj.useragent
        
    def ip_(self, obj):
        "Hack to fix encoding problem"
        return '<a href="%s/">%s</a>' % (str(obj.ip).replace('/', '_2F'), str(obj))
    ip_.allow_tags = True
    ip_.short_description = 'IP/Network'
        
def admin_bulk(request, flag):
    try:
        title = FLAGS_DICT[int(flag)]
    except None:
        return HttpResponseRedirect('../../')    
    form = BulkForm(flag, request.POST)
    if form.is_valid():
        form.save()
        success(request, 'Successfully saved %s.' % title.lower())
        if request.POST.get('_save'):
            return HttpResponseRedirect('../../')
    return render(request, 'admin/sentinel/bulk.html', locals())

admin.site.register(Address, AddressAdmin)
