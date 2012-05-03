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
from xml.dom.minidom import parseString

class Fact(models.Model):
    name = models.CharField(max_length=765)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'fact_names'
        ordering = [ 'name' ]

    def __unicode__(self):
        return self.name.replace('_',' ').rstrip()

class Host(models.Model):
    name = models.CharField(max_length=765)
    ip = models.CharField(max_length=765, blank=True)
    last_compile = models.DateTimeField(null=True, blank=True)
    last_freshcheck = models.DateTimeField(null=True, blank=True)
    last_report = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    source_file_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    facts = models.ManyToManyField(Fact, through='FactValue')

    class Meta:
        db_table = u'hosts'
        ordering = ['name',]

    def __unicode__(self):
        return self.name

    def get_fact_value(self, fact, default=None):
        try:
            return self.factvalue_set.get(fact_name__name=fact).value
        except:
            return default


class FactValue(models.Model):
    value = models.TextField()
    fact_name = models.ForeignKey(Fact)
    host = models.ForeignKey(Host)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'fact_values'

    def __unicode__(self):
        return "%s %s: %s" % (self.host.name, str(self.fact_name), self.value)

class ParamNames(models.Model):
    name = models.CharField(max_length=765)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'param_names'

class ParamValues(models.Model):
    value = models.TextField()
    param_name_id = models.IntegerField()
    line = models.IntegerField(null=True, blank=True)
    resource_id = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'param_values'

class PuppetTags(models.Model):
    name = models.CharField(max_length=765, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'puppet_tags'

class ResourceTags(models.Model):
    resource_id = models.IntegerField(null=True, blank=True)
    puppet_tag_id = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'resource_tags'

class Resources(models.Model):
    title = models.TextField()
    restype = models.CharField(max_length=765)
    host_id = models.IntegerField(null=True, blank=True)
    source_file_id = models.IntegerField(null=True, blank=True)
    exported = models.IntegerField(null=True, blank=True)
    line = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'resources'

class SourceFiles(models.Model):
    filename = models.CharField(max_length=765, blank=True)
    path = models.CharField(max_length=765, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'source_files'
