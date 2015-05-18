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
Unit tests for puppet package
'''

from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION[:2] >= (1, 3):
    from django.utils import unittest
else:
    import unittest

from django.test.client import Client
from puppet.models import Fact, Host, FactValue, ParamNames, ParamValues, PuppetTags, \
                    ResourceTags, SourceFile, Resource

# The following is an ugly hack for unit tests to work
# We force managed the unmanaged models so that tables will be created
Fact._meta.managed=True
Host._meta.managed=True
FactValue._meta.managed=True
ParamNames._meta.managed=True
ParamValues._meta.managed=True
PuppetTags._meta.managed=True
ResourceTags._meta.managed=True
SourceFile._meta.managed=True
Resource._meta.managed=True

class PuppetTestCase(unittest.TestCase):
    '''
    A test case for puppet database
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''

        self.sourcefile1 = SourceFile.objects.create(filename='testfile', path='/a/b/testfile.pp')
        self.fact1 = Fact.objects.create(name='TestFact')
        self.host1 = Host.objects.create(name='MyHost', ip='10.10.10.10', source_file=self.sourcefile1)
        self.resource1 = Resource.objects.create(title='TestResource', restype='testtype')
        self.factv1 = FactValue.objects.create(value='TestFactValue', fact_name=self.fact1, host=self.host1)
        self.param1 = ParamNames.objects.create(name='TestParam1')
        self.paramv1 = ParamValues.objects.create(value='TestParamValue', param_name=self.param1)
        self.puppettag1 = PuppetTags.objects.create(name='TestPuppetTag')
        self.resourcetag1 = ResourceTags.objects.create(puppet_tag=self.puppettag1)

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Fact.objects.all().delete()
        Host.objects.all().delete()
        FactValue.objects.all().delete()
        ParamNames.objects.all().delete()
        ParamValues.objects.all().delete()
        PuppetTags.objects.all().delete()
        ResourceTags.objects.all().delete()
        SourceFile.objects.all().delete()
        Resource .objects.all().delete()

    # Tests start here
    def test_if_fact_equal_with_self(self):
        self.assertEqual(self.factv1.name, self.factv1.fact_name.name)

class PuppetViewsTestCase(unittest.TestCase):
    '''
    A test case for servermon package
    '''
    def setUp(self):
        '''
        Commands run before every test
        '''
        self.host1 = Host.objects.create(name='testservermonHost1', ip='10.10.10.10')
        self.host2 = Host.objects.create(name='testservermonHost2', ip='10.10.10.10')
        self.fact1 = Fact.objects.create(name='memorysize')
        self.fact2 = Fact.objects.create(name='manufacturer')
        self.factv1 = FactValue.objects.create(value='TestFactValue1', fact_name=self.fact1, host=self.host1)
        self.factv2 = FactValue.objects.create(value='TestFactValue2', fact_name=self.fact2, host=self.host2)

    def tearDown(self):
        '''
        Commands run after every test
        '''
        Host.objects.all().delete()
        Fact.objects.all().delete()
        FactValue.objects.all().delete()


    def test_inventory(self):
        c = Client()
        response = c.get('/inventory/')
        self.assertEqual(response.status_code, 200)

    def test_query_get(self):
        c = Client()
        response = c.get('/query/')
        self.assertEqual(response.status_code, 200)

    def test_query_post_empty(self):
        c = Client()
        response = c.post('/query/')
        self.assertEqual(response.status_code, 200)

    def test_query_post_filled(self):
        c = Client()
        response = c.post('/query/', {'facts': (self.fact1.pk, self.fact2.pk), 'hosts': (self.host1.pk, self.host2.pk)})
        self.assertEqual(response.status_code, 200)
