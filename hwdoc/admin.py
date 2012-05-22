# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.

from django.contrib import admin
from servermon.hwdoc.models import *

class RoleInline(admin.TabularInline):
    model = Role
    extra = 1

class ProjectAdmin(admin.ModelAdmin):
    inlines = (RoleInline, )


class EmailInline(admin.TabularInline):
    model = Person.emails.through
    extra = 1

class PhoneInline(admin.TabularInline):
    model = Person.phones.through
    extra = 1
        
class EmailAdmin(admin.ModelAdmin):
    inlines = [ EmailInline ]

class PhoneAdmin(admin.ModelAdmin):
    inlines = [ PhoneInline ]

class PersonAdmin(admin.ModelAdmin):
    inlines = [ EmailInline, PhoneInline, RoleInline]
    search_fields = ('name', 'surname')
    exclude = ('phones', 'emails')

admin.site.register(Email, EmailAdmin)
admin.site.register(Phone, PhoneAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Project, ProjectAdmin)

admin.site.register(Vendor)
admin.site.register(Model)

def shutdown(modeladmin, request, queryset):
    for obj in queryset:
        try:
            obj.servermanagement
        except ServerManagement.DoesNotExist:
            continue
        obj.servermanagement.power_off_acpi()

shutdown.short_description = 'Shuts down an equipment'

def startup(modeladmin, request, queryset):
    for obj in queryset:
        try:
            obj.servermanagement
        except ServerManagement.DoesNotExist:
            continue
        obj.servermanagement.power_on()

startup.short_description = 'Starts up an equipment'

def shutdown_force(modeladmin, request, queryset):
    for obj in queryset:
        try:
            obj.servermanagement
        except ServerManagement.DoesNotExist:
            continue
        obj.servermanagement.power_off()

shutdown_force.short_description = 'Force a shutdown of an equipment'

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
    model_u.short_description = 'Us'

    list_display = ('allocation', 'model', 'serial',
            'rack', 'unit', model_u,
            mgmt_method, mgmt_username, mgmt_password,
            'purpose', 'state')
    list_display_links = ('serial',)
    list_filter = ('model', 'rack','state',)
    search_fields = ['rack', 'unit', 'serial', 'allocation__name']
    list_editable = ['allocation', 'state']
    ordering = ('rack', 'unit',)
    inlines = [ ServerManagementInline, ]
    actions = [ shutdown, startup, shutdown_force ]

admin.site.register(Equipment, EquipmentAdmin)
