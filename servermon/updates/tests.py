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
from django.core.management import call_command

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
        print self.host1
        self.package1 = Package.objects.create(name='testpackage', sourcename='testsource')
        self.package2 = Package.objects.create(name='testpackage', sourcename='testpackage')
        print self.package1
        print self.package2
        self.update1 = Update.objects.create(package=self.package1, host=self.host1,
                installedVersion = '1.1', candidateVersion='1.2',
                source = 'TestSource', origin='Debian')
        self.update2 = Update.objects.create(package=self.package2, host=self.host1,
                installedVersion = '1.1', candidateVersion='1.2',
                source = 'TestSource', origin='Ubuntu')
        print self.update1
        print self.update1.get_changelog_url()
        print self.update2
        print self.update2.get_changelog_url()

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Host.objects.all().delete()
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
        self.fact1 = Fact.objects.create(name='interfaces')
        self.fact2 = Fact.objects.create(name='macaddress_eth0')
        self.fact3 = Fact.objects.create(name='ipaddress_eth0')
        self.fact4 = Fact.objects.create(name='netmask_eth0')
        self.fact5 = Fact.objects.create(name='ipaddress6_eth0')
        self.factvalue1 = FactValue.objects.create(value='eth0',
                fact_name=self.fact1, host=self.host1)
        self.factvalue2 = FactValue.objects.create(value='aa:bb:cc:dd:ee:ff',
                fact_name=self.fact2, host=self.host1)
        self.factvalue3 = FactValue.objects.create(value='10.10.10.10',
                fact_name=self.fact3, host=self.host1)
        self.factvalue4 = FactValue.objects.create(value='255.255.255.0',
                fact_name=self.fact4, host=self.host1)
        self.factvalue5 = FactValue.objects.create(value='dead:beef::1/64',
                fact_name=self.fact5, host=self.host1)

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Package.objects.all().delete()
        Host.objects.all().delete()
        Fact.objects.all().delete()
        FactValue.objects.all().delete()

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

class CommandsTestCase(unittest.TestCase):
    '''
    A test case for django management commands
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''
        self.package1 = Package.objects.create(name='testpackage', sourcename='testsource')
        self.package2 = Package.objects.create(name='testpackage2', sourcename='testsource')
        self.host1 = Host.objects.create(name='testservermonHost1', ip='10.10.10.10')
        self.fact1 = Fact.objects.create(name='interfaces')
        self.fact2 = Fact.objects.create(name='macaddress_eth0')
        self.fact3 = Fact.objects.create(name='ipaddress_eth0')
        self.fact4 = Fact.objects.create(name='netmask_eth0')
        self.fact5 = Fact.objects.create(name='ipaddress6_eth0')
        self.factvalue1 = FactValue.objects.create(value='eth0',
                fact_name=self.fact1, host=self.host1)
        self.factvalue2 = FactValue.objects.create(value='aa:bb:cc:dd:ee:ff',
                fact_name=self.fact2, host=self.host1)
        self.factvalue3 = FactValue.objects.create(value='10.10.10.10',
                fact_name=self.fact3, host=self.host1)
        self.factvalue4 = FactValue.objects.create(value='255.255.255.0',
                fact_name=self.fact4, host=self.host1)
        self.factvalue5 = FactValue.objects.create(value='dead:beef::1/64',
                fact_name=self.fact5, host=self.host1)

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Package.objects.all().delete()
        Host.objects.all().delete()
        Fact.objects.all().delete()
        FactValue.objects.all().delete()

    def test_make_updates(self):
        call_command('make_updates')
