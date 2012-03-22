# vim: ts=4 sts=4 et ai sw=4 fileencoding=utf-8

from django.contrib import admin
from servermon.hwdoc.models import *

admin.site.register(Vendor)
admin.site.register(Model)

class ServerManagementInline(admin.StackedInline):
    model = ServerManagement

class EquipmentAdmin(admin.ModelAdmin):
    def mgmt_method(obj):
        return obj.servermanagement.get_method_display()
    mgmt_method.short_description = 'OOB Method'

    def mgmt_username(obj):
        return obj.servermanagement.username
    mgmt_username.short_description = 'OOB Username'

    def mgmt_password(obj):
        return obj.servermanagement.password
    mgmt_password.short_description = 'OOB Password'

    def model_u(obj):
        return obj.model.u
    model_u.short_description = 'Unit Height'

    list_display = ('purpose', 'model', 'serial',
            'rack', 'unit', model_u,
            mgmt_method, mgmt_username, mgmt_password,
            'comments', 'updated')
    list_display_links = ('serial',)
    list_filter = ('model', 'rack')
    ordering = ('rack', 'unit',)
    inlines = [ ServerManagementInline, ]

admin.site.register(Equipment, EquipmentAdmin)
