# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2012 Faidon Liambotis
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
puppet module's functions documentation. This has been create by django
inspecting the puppet database
'''

from django.db import models
from django.conf import settings

# We check from settings whether the puppet models should be managed or not.
# Default is false
MANAGED_PUPPET_MODELS = getattr(settings, 'MANAGED_PUPPET_MODELS', False)


class SourceFile(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

    filename = models.CharField(max_length=255, blank=True)
    path = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'source_files'
        managed = MANAGED_PUPPET_MODELS


class Fact(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'fact_names'
        ordering = ['name']
        managed = MANAGED_PUPPET_MODELS

    def __unicode__(self):
        '''
        Get a string representation of the instance
        '''

        return self.name.replace('_', ' ').rstrip()


class Host(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

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
        ordering = ['name', ]
        managed = MANAGED_PUPPET_MODELS

    def __unicode__(self):
        '''
        Get a string representation of the instance
        '''

        return self.name

    def get_fact_value(self, fact, default=None):
        '''
        Get the value of a fact
        '''

        try:
            return self.factvalue_set.get(fact_name__name=fact).value
        except:
            return default


class Resource(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

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
        managed = MANAGED_PUPPET_MODELS


class FactValue(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

    value = models.TextField()
    fact_name = models.ForeignKey(Fact)
    host = models.ForeignKey(Host)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'fact_values'
        managed = MANAGED_PUPPET_MODELS

    @property
    def name(self):
        '''
        Property returning the fact name
        '''

        return self.fact_name.name

    def __unicode__(self):
        '''
        Get a string representation of the instance
        '''

        return "%s %s: %s" % (self.host.name, str(self.fact_name), self.value)


class ParamNames(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'param_names'
        managed = MANAGED_PUPPET_MODELS


class ParamValues(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

    value = models.TextField()
    param_name = models.ForeignKey(ParamNames)
    line = models.IntegerField(null=True, blank=True)
    resource = models.ForeignKey(Resource, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'param_values'
        managed = MANAGED_PUPPET_MODELS


class PuppetTags(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

    name = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'puppet_tags'
        managed = MANAGED_PUPPET_MODELS


class ResourceTags(models.Model):
    '''
    Modeling the respective puppet concept.
    '''

    resource = models.ForeignKey(Resource, null=True, blank=True)
    puppet_tag = models.ForeignKey(PuppetTags, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = u'resource_tags'
        managed = MANAGED_PUPPET_MODELS
