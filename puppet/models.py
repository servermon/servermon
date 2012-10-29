# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2012 Faidon Liambotis
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

class SourceFile(models.Model):
    filename = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'source_files'
        managed = False

class Fact(models.Model):
    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'fact_names'
        ordering = [ 'name' ]
        managed = False

    def __unicode__(self):
        return self.name.replace('_',' ').rstrip()

class Host(models.Model):
    name = models.CharField(max_length=255)
    ip = models.CharField(max_length=255, blank=True)
    environment = models.CharField(max_length=255, blank=True)
    last_compile = models.DateTimeField(null=True, blank=True)
    last_freshcheck = models.DateTimeField(null=True, blank=True)
    last_report = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    source_file = models.ForeignKey(SourceFile, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    facts = models.ManyToManyField(Fact, through='FactValue')

    class Meta:
        db_table = u'hosts'
        ordering = ['name',]
        managed = False

    def __unicode__(self):
        return self.name

    def get_fact_value(self, fact, default=None):
        try:
            return self.factvalue_set.get(fact_name__name=fact).value
        except:
            return default

class Resource(models.Model):
    title = models.TextField()
    restype = models.CharField(max_length=255)
    host = models.ForeignKey(Host, null=True, blank=True)
    source_file = models.ForeignKey(SourceFile, null=True, blank=True)
    exported = models.IntegerField(null=True, blank=True)
    line = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'resources'
        managed = False

class FactValue(models.Model):
    value = models.TextField()
    fact_name = models.ForeignKey(Fact)
    host = models.ForeignKey(Host)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'fact_values'
        managed = False

    @property
    def name(self):
        return self.fact_name.name

    def __unicode__(self):
        try:
            return "%s %s: %s" % (self.host.name, str(self.fact_name), self.value)
        except Exception:
            return "(unknown host) %s: %s" % (str(self.fact_name), self.value)

class ParamNames(models.Model):
    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'param_names'
        managed = False

class ParamValues(models.Model):
    value = models.TextField()
    param_name = models.ForeignKey(ParamNames)
    line = models.IntegerField(null=True, blank=True)
    resource = models.ForeignKey(Resource, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'param_values'
        managed = False

class PuppetTags(models.Model):
    name = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'puppet_tags'
        managed = False

class ResourceTags(models.Model):
    resource = models.ForeignKey(Resource, null=True, blank=True)
    puppet_tag = models.ForeignKey(PuppetTags, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'resource_tags'
        managed = False

