# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
'''
hwdoc module's functions documentation. Main models are Equipment and ServerManagement
'''

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from keyvalue.models import KeyValue


# Allocation models #
class Email(models.Model):
    '''
    Email Model. Represents an email. No special checks are done for user input
    '''

    email = models.CharField(max_length=80)

    class Meta:
        verbose_name = _(u'Email')
        verbose_name_plural = _(u'Emails')

    def __unicode__(self):
        return self.email


class Phone(models.Model):
    '''
    Phone Model. Represents a phone. No special checks are done for user input
    '''

    number = models.CharField(max_length=80)

    class Meta:
        verbose_name = _(u'Phone')
        verbose_name_plural = _(u'Phones')

    def __unicode__(self):
        return self.number


class Person(models.Model):
    '''
    Person Model. Represents a Person with relations to Email, Phone
    No special checks are done for user input
    '''

    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    emails = models.ManyToManyField(Email)
    phones = models.ManyToManyField(Phone)

    class Meta:
        verbose_name = _(u'Person')
        verbose_name_plural = _(u'People')

    def __unicode__(self):
        result = u'%s %s ' % (self.name, self.surname)
        if self.emails.count() > 0:
            result += u'<%s> ' % ', '.join(map(lambda x: x[0], self.emails.values_list('email')))
        if self.phones.count() > 0:
            result += u'%s' % ', '.join(map(lambda x: x[0], self.phones.values_list('number')))
        return result


class Project(models.Model):
    '''
    Project Model. The idea is to allocate Equipments to Projects
    '''

    name = models.CharField(max_length=80)
    contacts = models.ManyToManyField(Person, through='Role')

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u'Project')
        verbose_name_plural = _(u'Projects')

    def __unicode__(self):
        return self.name


class Role(models.Model):
    '''
    Roles for projects
    '''

    ROLES = (
        ('manager', 'Manager'),
        ('technical', 'Techinal Person'),
    )
    role = models.CharField(max_length=80, choices=ROLES)
    project = models.ForeignKey(Project)
    person = models.ForeignKey(Person)

    class Meta:
        verbose_name = _(u'Role')
        verbose_name_plural = _(u'Roles')

    def __unicode__(self):
        return _(u'Project: %(project)s, Person: %(name)s %(surname)s, Role: %(role)s') % {
            'project': self.project.name,
            'name': self.person.name,
            'surname': self.person.surname,
            'role': self.role,
        }


# Equipment models #
class Datacenter(models.Model):
    '''
    Datacenters
    '''

    name = models.CharField(max_length=20)

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u'Datacenter')
        verbose_name_plural = _(u'Datacenters')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('hwdoc.views.datacenter', [str(self.id)])


class Vendor(models.Model):
    '''
    Equipments have Models and belong to Vendors
    '''

    name = models.CharField(max_length=80)

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u'Vendor')
        verbose_name_plural = _(u'Vendors')

    def __unicode__(self):
        return self.name


class Model(models.Model):
    '''
    Abstract class for all vendor models
    '''

    vendor = models.ForeignKey(Vendor)
    name = models.CharField(max_length=80)

    class Meta:
        abstract = True
        verbose_name = _(u'Model')
        verbose_name_plural = _(u'Models')


class RackModel(Model):
    '''
    Rack vendor models
    '''

    max_mounting_depth = models.PositiveIntegerField(max_length=10)
    min_mounting_depth = models.PositiveIntegerField(max_length=10)
    height = models.PositiveIntegerField(max_length=10)
    width = models.PositiveIntegerField(max_length=10)
    inrow_ac = models.BooleanField(default=False)

    class Meta:
        verbose_name = _(u'Rack Model')
        verbose_name_plural = _(u'Rack Models')

    def __unicode__(self):
        return u'%s %s' % (self.vendor, self.name)

    @property
    def units(self):
        return reversed(range(1, self.height + 1))


class Rack(models.Model):
    '''
    Racks
    '''

    mounted_depth = models.PositiveIntegerField(max_length=10, default=60)
    model = models.ForeignKey(RackModel)
    name = models.CharField(max_length=80)

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u'Rack')
        verbose_name_plural = _(u'Racks')

    def __unicode__(self):
        return u'%s' % (self.name)

    def get_empty_units(self, related=None):
        '''
        Calculates the empty units in a rack and returns them in a list

        @type  self: Rack
        @param self: An Instance of Model Rack

        @rtype: list
        @return: A list with empty units
        '''

        equipment_list = self.equipment_set.all()
        if related:
            equipment_list = equipment_list.select_related(*related)
        units = []
        for z in ((x + w for w in range(y)) for x, y in equipment_list.values_list('unit', 'model__u')):
            units.extend(z)
        empty_units = set(self.model.units) - set(sorted(units))
        return empty_units

    @models.permalink
    def get_absolute_url(self):
        return ('hwdoc.views.rack', [str(self.id)])


class RackRow(models.Model):
    '''
    Racks in a row are a RackRow
    '''

    name = models.CharField(max_length=80)
    dc = models.ForeignKey(Datacenter, null=True, blank=True)

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u'Rack Row')
        verbose_name_plural = _(u'Rack Rows')

    def __unicode__(self):
        return u'%s in %s' % (self.name, self.dc)


class Storage(models.Model):
    '''
    Datacenter may have storage facilities
    '''

    name = models.CharField(max_length=80, unique=True)
    dc = models.ForeignKey(Datacenter)

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u'Storage')
        verbose_name_plural = _(u'Storages')

    def __unicode__(self):
        return u'%s in %s' % (self.name, self.dc)


class RackPosition(models.Model):
    '''
    Racks can be positioned in a RackRow
    '''

    rack = models.OneToOneField(Rack)
    rr = models.ForeignKey(RackRow)
    position = models.PositiveIntegerField(max_length=20)

    class Meta:
        ordering = ['position', ]
        verbose_name = _(u'Rack Position in Rack Row')
        verbose_name_plural = _(u'Rack Positions in Rack Rows')

    def __unicode__(self):
        return _(u'Rack: %(rack)s, Position: %(position)02d, RackRow: %(rackrow)s') % {
            'rack': self.rack,
            'position': self.position,
            'rackrow': self.rr,
        }


class EquipmentModel(Model):
    '''
    Equipments have Models
    '''

    u = models.PositiveIntegerField(verbose_name="Us")
    attrs = generic.GenericRelation(KeyValue,
                                    content_type_field='owner_content_type',
                                    object_id_field='owner_object_id')

    class Meta:
        ordering = ['vendor', 'name', ]
        verbose_name = _(u'Equipment Model')
        verbose_name_plural = _(u'Equipment Models')

    def __unicode__(self):
        return u'%s %s' % (self.vendor, self.name)

    @property
    def units(self):
        return reversed(range(1, self.u + 1))


class Equipment(models.Model):
    '''
    Equipment model
    '''

    ORIENTATIONS = (
        ('Front', 'Front'),
        ('Back', 'Back'),
        ('NA', 'Not Applicable'),
    )

    model = models.ForeignKey(EquipmentModel)
    allocation = models.ForeignKey(Project, null=True, blank=True)
    serial = models.CharField(max_length=80, unique=True)
    rack = models.ForeignKey(Rack, null=True, blank=True)
    unit = models.PositiveIntegerField(null=True, blank=True)
    purpose = models.CharField(max_length=80, blank=True)
    rack_front = models.BooleanField(default=True)
    rack_interior = models.BooleanField(default=True)
    rack_back = models.BooleanField(default=True)
    orientation = models.CharField(max_length=10, choices=ORIENTATIONS, default='Front')
    storage = models.ForeignKey(Storage, null=True, blank=True)
    comments = models.TextField(blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    attrs = generic.GenericRelation(KeyValue,
                                    content_type_field='owner_content_type',
                                    object_id_field='owner_object_id')

    class Meta:
        ordering = ['rack', '-unit']
        permissions = (
            ('can_change_comment', 'Can change comments'),
        )
        verbose_name = _(u'Equipment')
        verbose_name_plural = _(u'Equipments')

    def __unicode__(self):
        out = u''
        if self.purpose:
            out += u'%s, ' % self.purpose
        out += u'%s ' % self.model
        if self.rack and self.unit:
            out += u'@ %sU%.2d ' % (self.rack, self.unit)
        out += u'(%s)' % self.serial
        return out

    @property
    def dc(self):
        if self.rack:
            return self.rack.rackposition.rr.dc
        elif self.storage:
            return self.storage.dc
        else:
            return None


class ServerManagement(models.Model):
    '''
    Equipments that can be managed have a ServerManagement counterpanrt
    '''

    equipment = models.OneToOneField(Equipment)
    METHODS = (
        ('ilo2', 'HP iLO 2'),
        ('ilo3', 'HP iLO 3'),
        ('irmc', 'Fujitsu iRMC'),
        ('idrac', 'Dell iDRAC'),
        ('ipmi', 'Generic IPMI'),
        ('dummy', 'Dummy Method Backend'),
    )
    method = models.CharField(choices=METHODS, max_length=10)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    hostname = models.CharField(max_length=80)
    username = models.CharField(max_length=80, blank=True)
    password = models.CharField(max_length=80, blank=True)
    license = models.CharField(max_length=80, blank=True)
    raid_license = models.CharField(max_length=80, blank=True)
    mac = models.CharField(max_length=17, blank=True)

    class Meta:
        verbose_name = _(u'Server Management')
        verbose_name_plural = _(u'Servers Management')

    def __unicode__(self):
        return '%s for %s' % (self.get_method_display(), self.equipment)

    def __sm__(self, action, username, password, **kwargs):
        if username is None:
            username = self.username
        if password is None:
            password = self.password
        if action == 'license_set' and ('license' not in kwargs or kwargs['license'] is None):
            kwargs['license'] = self.license

        try:
            sm = __import__('hwdoc.vendor.bmc_%s' % self.method, fromlist=['hwdoc.vendor'])
        except ImportError as e:
            # TODO: Log the error. For now just print
            print e
            return

        try:
            return getattr(sm, action)(self.hostname, username, password, **kwargs)
        except AttributeError as e:
            # TODO: Log the error. For now just print
            print e
            return

    def power_on(self, username=None, password=None, **kwargs):
        '''
        Power on a server
        '''

        return self.__sm__('power_on', username, password, **kwargs)

    def power_off(self, username=None, password=None, **kwargs):
        '''
        Power off a server
        '''

        return self.__sm__('power_off', username, password, **kwargs)

    def power_cycle(self, username=None, password=None, **kwargs):
        '''
        Power cycle a server
        '''

        return self.__sm__('power_cycle', username, password, **kwargs)

    def power_reset(self, username=None, password=None, **kwargs):
        '''
        Power reset a server
        '''

        return self.__sm__('power_reset', username, password, **kwargs)

    def power_off_acpi(self, username=None, password=None, **kwargs):
        '''
        Power off by sending an ACPI signal
        '''

        return self.__sm__('power_off_acpi', username, password, **kwargs)

    def pass_change(self, username=None, password=None, **kwargs):
        '''
        Change password for an OOB account
        '''

        return self.__sm__('pass_change', username, password, **kwargs)

    def set_settings(self, username=None, password=None, **kwargs):
        '''
        Set OOB settings
        '''

        return self.__sm__('set_settings', username, password, **kwargs)

    def set_ldap_settings(self, username=None, password=None, **kwargs):
        '''
        Set OOB LDAP Settings
        '''

        return self.__sm__('set_ldap_settings', username, password, **kwargs)

    def boot_order(self, username=None, password=None, **kwargs):
        '''
        Set Boot order. One time boot if support can be enabled
        '''

        return self.__sm__('boot_order', username, password, **kwargs)

    def license_set(self, username=None, password=None, **kwargs):
        '''
        Set license for OOB if applicable
        '''

        return self.__sm__('license_set', username, password, **kwargs)

    def bmc_reset(self, username=None, password=None, **kwargs):
        '''
        Reset a BMC
        '''

        return self.__sm__('bmc_reset', username, password, **kwargs)

    def bmc_factory_defaults(self, username=None, password=None, **kwargs):
        '''
        Reset a BMC to factory defaults
        '''

        return self.__sm__('bmc_factory_defaults', username, password, **kwargs)

    def add_user(self, username=None, password=None, **kwargs):
        '''
        Add a User to the bmc
        '''

        return self.__sm__('add_user', username, password, **kwargs)

    def remove_user(self, username=None, password=None, **kwargs):
        '''
        Remove a User from the bmc
        '''

        return self.__sm__('remove_user', username, password, **kwargs)

    def get_all_users(self, username=None, password=None, **kwargs):
        '''
        Get a list of all Users configured in the BMC
        '''

        return self.__sm__('get_all_users', username, password, **kwargs)

    def firmware_update(self, username=None, password=None, **kwargs):
        '''
        Perform a firmware update of the BMC
        '''

        return self.__sm__('firmware_update', username, password, **kwargs)

# Auxiliary models


class Ticket(models.Model):
    '''
    A ticket associated with a model
    '''
    STATES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    name = models.CharField(max_length=20, unique=True)
    state = models.CharField(choices=STATES, max_length=10)
    equipment = models.ManyToManyField(Equipment)
    url = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = _(u'Ticket')
        verbose_name_plural = _(u'Tickets')

    def __unicode__(self):
        return u'Ticket: %s' % (self.name)

    def closed(self):
        if self.state == 'closed':
            return True
        return False
