from django.conf.urls.defaults import patterns
from django.contrib.messages import success
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from models import *
from flags import *
from forms import BulkForm

class AddressAdmin(admin.ModelAdmin):
    list_display = ('ip', 'flag', 'useragent_', 'updated')
    list_filter = ('flag', 'is_network', 'updated', )
    search_fields = ('ip', 'useragent', )
    readonly_fields = ('useragent', 'count', 'created', 'updated', )
    actions = ['delete_selected', 'whitelist', 'greylist', 'blacklist', 'brownlist']

    @staticmethod
    def _list(qs, flag):
        qs.update(flag=flag)
        load_flags(qs)
        return "%s %sed." % (len(qs), FLAGS_DICT[flag].lower())
    
    def whitelist(self, request, queryset):
        self.message_user(request, self._list(queryset, WHITE))
    whitelist.short_description = "Whitelist"

    def greylist(self, request, queryset):
        self.message_user(request, self._list(queryset, GREY))
    greylist.short_description = "Greylist"

    def blacklist(self, request, queryset):
        self.message_user(request, self._list(queryset, BLACK))
    blacklist.short_description = "Blacklist"

    def brownlist(self, request, queryset):
        self.message_user(request, self._list(queryset, BROWN))
    brownlist.short_description = "Brownlist"
        
    def get_urls(self):
        urls = super(AddressAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^reload/$', reload_flags),
            (r'^bulk/(\d)/$', admin_bulk),
        )
        return my_urls + urls
    
    def useragent_(self, obj):
        TRIM = 100
        if len(obj.useragent) > TRIM:
            return '%s...'%obj.useragent[:TRIM]
        return obj.useragent
        
def reload_flags(request):
    msg = load_flags()
    messages.success(request, 'Successfully %s' % msg)
    return HttpResponseRedirect('..')
    
def admin_bulk(request, flag):
    try:
        title = FLAGS_DICT[int(flag)]
    except None:
        return HttpResponseRedirect('../../')    
    form = BulkForm(flag, request.POST)
    if form.is_valid():
        form.save()
        success(request, 'Successfully saved %s.' % title.lower())
        url = '.'
        if request.POST.get('_save'):
            url = '../../'
        return HttpResponseRedirect(url)
    return render(request, 'admin/sentinel/bulk.html', locals())

admin.site.register(Address, AddressAdmin)
