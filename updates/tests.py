# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
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
'''
Unit tests for updates package
'''

from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION[:2] >= (1, 3):
    from django.utils import unittest
else:
    import unittest

from puppet.models import Host, Resource, FactValue, Fact
from updates.models import Package, Update
from django.test.client import Client

# The following is an ugly hack for unit tests to work
# We force managed the unmanaged models so that tables will be created
Host._meta.managed = True
Resource._meta.managed = True
FactValue._meta.managed = True
Fact._meta.managed = True

class UpdatesTestCase(unittest.TestCase):
    '''
    A test case for updates app 
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''

        self.host1 = Host.objects.create(name='MyHost', ip='10.10.10.10')
        self.package1 = Package.objects.create(name='testpackage', sourcename='testsource')
        self.update1 = Update.objects.create(package=self.package1, host=self.host1,
                installedVersion = '1.1', candidateVersion='1.2',
                source = 'TestSource', origin='Debian')

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Package.objects.all().delete()
        Update.objects.all().delete()

    # Tests start here
    def test_if_host_equal(self):
        self.assertEqual(self.update1.host.name, self.package1.hosts.all()[0].name)

class ViewsTestCase(unittest.TestCase):
    '''
    Testing views class
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''

        self.package1 = Package.objects.create(name='testpackage', sourcename='testsource')
        self.package2 = Package.objects.create(name='testpackage2', sourcename='testsource')
        self.host1 = Host.objects.create(name='testservermonHost1', ip='10.10.10.10')

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Package.objects.all().delete()
        Host.objects.all().delete()

    def test_hostlist(self):
        c = Client()
        response = c.get('/hosts/')
        self.assertEqual(response.status_code, 200)

    def test_packagelist(self):
        c = Client()
        response = c.get('/packages/')
        self.assertEqual(response.status_code, 200)

    def test_empty_package(self):
        c = Client()
        data = ['']
        for d in data:
            response = c.get('/packages/%s' % d)
            # This is not an error since empty package means, due to 
            # urls.py that we fallback to packagelist
            self.assertEqual(response.status_code, 200)

    def test_nonexistent_package(self):
        c = Client()
        data = ['nosuchpackage']
        for d in data:
            response = c.get('/packages/%s' % d)
            self.assertEqual(response.status_code, 404)

    def test_existent_package(self):
        c = Client()
        data = [self.package1.name, self.package2.name]
        for d in data:
            response = c.get('/packages/%s' % d)
            self.assertEqual(response.status_code, 200)

    def test_empty_host(self):
        c = Client()
        response = c.get('/hosts/%s' % '')
        # This should work because of urls fallback to hostlist
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_host(self):
        c = Client()
        response = c.get('/hosts/%s' % 'nosuchhost' )
        self.assertEqual(response.status_code, 404)

    def test_existent_host(self):
        c = Client()
        data = [self.host1.name]
        for d in data:
            response = c.get('/hosts/%s' % d)
            self.assertEqual(response.status_code, 200)

# This is here because there are some servermon wide views which must
# be moved in the updates app. 
class ServermonViewsTestCase(unittest.TestCase):
    '''
    A test case for servermon package 
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''
        self.host1 = Host.objects.create(name='testservermonHost1', ip='10.10.10.10')
        self.host2 = Host.objects.create(name='testservermonHost2', ip='10.10.10.10')
        self.fact1 = Fact.objects.create(name='TestFact1')
        self.fact2 = Fact.objects.create(name='TestFact2')
        self.factv1 = FactValue.objects.create(value='TestFactValue1', fact_name=self.fact1, host=self.host1)
        self.factv2 = FactValue.objects.create(value='TestFactValue2', fact_name=self.fact2, host=self.host2)

    def tearDown(self):
        '''
        Commands run after every test
        '''
        self.host1.delete()

    def test_inventory(self):
        c = Client()
        response = c.get('/inventory/')
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_incorrect_search(self):
        c = Client()
        response = c.post('/search/')
        self.assertEqual(response.status_code, 302)

    def test_correct_search(self):
        c = Client()
        response = c.post('/search/', {'search': self.host1.name})
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
