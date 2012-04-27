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

from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=80)

    def __unicode__(self):
        return self.name

class Model(models.Model):
    vendor = models.ForeignKey(Vendor)
    name = models.CharField(max_length=80)
    u = models.PositiveIntegerField(verbose_name="Us")

    def __unicode__(self):
        return "%s %s" % (self.vendor, self.name)

class Equipment(models.Model):
    STATE = (
            ('0', 'WORKING - OK'),
            ('1', 'WORKING - RMA'),
            ('2', 'NOT-WORKING - RMA'),
            ('3', 'NOT-WORKING - CHECKING'),
            ('4', 'INACTIVE'),
            ('5', 'UNKNOWN'),
        )
    model = models.ForeignKey(Model)
    serial = models.CharField(max_length=80)
    rack = models.PositiveIntegerField(null=True, blank=True)
    unit = models.PositiveIntegerField(null=True, blank=True)
    purpose = models.CharField(max_length=80, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(choices=STATE,null=True, blank=True, max_length=20)

    def __unicode__(self):
        out = ""
        if self.purpose:
            out += "%s, " % self.purpose
        out += "%s " % self.model
        if self.rack and self.unit:
            out += "@ R%.2dU%.2d " % (self.rack, self.unit)
        out += "(%s)" % self.serial
        return out

class ServerManagement(models.Model):
    equipment = models.OneToOneField(Equipment)
    METHODS = (
            ('ilo2', 'HP iLO 2'),
            ('ilo3', 'HP iLO 3'),
            ('irmc', 'Fujitsu iRMC'),
            ('ipmi', 'Generic IPMI'),
        )
    method = models.CharField(choices=METHODS, max_length=10)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    hostname = models.CharField(max_length=80)
    username = models.CharField(max_length=80, null=True, blank=True)
    password = models.CharField(max_length=80, null=True, blank=True)
    license = models.CharField(max_length=80, null=True, blank=True)
    raid_license = models.CharField(max_length=80, null=True, blank=True)
    mac = models.CharField(max_length=17, null=True, blank=True)

    def __unicode__(self):
        return "%s for %s" % (self.get_method_display(), self.equipment)

    def __sm__(self, action, username, password):
        if username is None:
            username = self.username
        if password is None:
            password = self.password

        try:
            sm = __import__('hwdoc.vendor.' + self.method, fromlist=['hwdoc.vendor']) 
        except ImportError as e:
            # TODO: Log the error. For now just print 
            print e
            return
        
        try:
            getattr(sm, action)(self.hostname, username, password)
        except AttributeError as e:
            # TODO: Log the error. For now just print 
            print e
            return

    def power_on(self, username=None, password=None):
        return self.__sm__('power_on', username, password)

    def power_off(self, username=None, password=None):
        return self.__sm__('power_off', username, password)

    def power_cycle(self, username=None, password=None):
        return self.__sm__('power_cycle', username, password)

    def power_reset(self, username=None, password=None):
        return self.__sm__('power_reset', username, password)

    def power_off_acpi(self, username=None, password=None):
        return self.__sm__('power_off_acpi', username, password)
