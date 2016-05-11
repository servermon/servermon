# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2013 Alexandros Kosiaris
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
keyvalue module's documentation.
Each keyvalue has three items.
 1. An owner which must be an instance of a django model
 2. A key, which must be an instance of keyvalue.models.Key
 3. A value, which is a charfield
'''

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Key(models.Model):
    '''
    The key part of the key value pair
    '''

    name = models.CharField(max_length=50, help_text='Name of the KeyValue', unique=True)
    verbose_name = models.CharField(max_length=100, blank=True, help_text='Human readable version of the name')
    description = models.CharField(max_length=150, blank=True, help_text='Description of what this key represents')

    def __unicode__(self):
        if self.description != u'':
            return u'%s - %s' % (self.name, self.description)
        return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        if self.verbose_name == u'':
            verbose_name = self.name.title()
            verbose_name = verbose_name.replace('-', ' ')
            verbose_name = verbose_name.replace('_', ' ')
            self.verbose_name = verbose_name.replace('.', ' ')
        super(Key, self).save(*args, **kwargs)


class KeyValue(models.Model):
    '''
    Attach a key and a value to any instance of any django model.
    '''

    key = models.ForeignKey(Key)
    value = models.CharField(max_length=255, blank=True)

    owner_content_type = models.ForeignKey(ContentType)
    owner_object_id = models.PositiveIntegerField()
    owner_content_object = generic.GenericForeignKey('owner_content_type', 'owner_object_id')

    class Meta:
        unique_together = ('key', 'owner_content_type', 'owner_object_id')

    @property
    def name(self):
        return self.key.name

    @property
    def verbose_name(self):
        return self.key.verbose_name

    @property
    def description(self):
        return self.key.description

    @property
    def owner(self):
        return self.owner_content_object

    def __unicode__(self):
        res = u'%s = %s on %s' % (
            self.key.name,
            self.value,
            self.owner_content_object)
        return res
