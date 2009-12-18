from virt.models import *
from django.contrib import admin

class NodeInline(admin.TabularInline):
    model = Node
    exclude = ('notes',)
    extra = 4

class ClusterAdmin(admin.ModelAdmin):
    model = Cluster
    inlines = [NodeInline]


class NodeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,  {'fields': ['host', 'cluster', 'notes']}),
        ('Network access', {'fields': ['transport'] })
        #('mpe', {'fields': ['kot'] }),
    ]
    list_display = ('hostname', 'cluster', 'notes', 'get_host_arch', 'status', 'has_kvm', 'has_qemu', 'has_xen', 'has_openvz')
    #list_filter = ('has_openvz', 'has_kvm', 'has_xen')
    list_filter = ('cluster',)

class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'node', 'cluster', 'type', 'os_type', 'memory', 'is_puppetized', 'last_seen', 'get_contacts')
    list_filter = ('node', 'cluster')


class DomainContactAdmin(admin.ModelAdmin):
    filter_horizontal = ['domains',]

admin.site.register(Node, NodeAdmin)
admin.site.register(Cluster, ClusterAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(DomainContact, DomainContactAdmin)
