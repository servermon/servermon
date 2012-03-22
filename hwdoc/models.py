# vim: ts=4 sts=4 et ai sw=4 fileencoding=utf-8

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
    model = models.ForeignKey(Model)
    serial = models.CharField(max_length=80)
    rack = models.PositiveIntegerField(null=True, blank=True)
    unit = models.PositiveIntegerField(null=True, blank=True)
    purpose = models.CharField(max_length=80, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
    mac = models.CharField(max_length=17, null=True, blank=True)

    def __unicode__(self):
        return "%s for %s" % (self.get_method_display(), self.equipment)
