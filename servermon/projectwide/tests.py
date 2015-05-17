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
Unit tests for projectwide package
'''

from django import VERSION as DJANGO_VERSION
import ldap
from mockldap import MockLdap

if DJANGO_VERSION[:2] >= (1, 3):
    from django.utils import unittest
else:
    import unittest

from puppet.models import Host, Resource, FactValue, Fact
from projectwide.functions import get_search_terms, canonicalize_mac
from django.test.client import Client

# The following is an ugly hack for unit tests to work
# We force managed the unmanaged models so that tables will be created
Host._meta.managed = True
Resource._meta.managed = True
FactValue._meta.managed = True
Fact._meta.managed = True

class FunctionsTestCase(unittest.TestCase):
    '''
    Testing functions class
    '''

    def test_mac_canonicalizer(self):
        self.assertEqual(canonicalize_mac('1111.2222.3333'), '11:11:22:22:33:33')
        self.assertEqual(canonicalize_mac('11-11-22-22-33-33'), '11:11:22:22:33:33')
        self.assertEqual(canonicalize_mac('11:11:22:22:33:33'), '11:11:22:22:33:33')

    def test_free_text_search(self):
        text=u'''
        This is a text that is not going to make any sense
        '''

        tokens = get_search_terms(text)
        self.assertNotEqual(len(tokens), 0)


class ProjectWideViewsTestCase(unittest.TestCase):
    '''
    A test case for projectwide package
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''
        self.host1 = Host.objects.create(name='testservermonHost1', ip='10.10.10.10')

    def tearDown(self):
        '''
        Commands run after every test
        '''
        Host.objects.all().delete()

    def test_index(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_incorrect_search(self):
        c = Client()
        response = c.post('/search/')
        self.assertEqual(response.status_code, 200)

    def test_correct_search(self):
        c = Client()
        response = c.post('/search/', {'q': self.host1.name})
        self.assertEqual(response.status_code, 200)

    def test_advanced_search(self):
        c = Client()
        response = c.post('/advancedsearch/')
        self.assertEqual(response.status_code, 200)

    def test_opensearch(self):
        c = Client()
        response = c.get('/opensearch.xml')
        self.assertEqual(response.status_code, 200)

    def test_opensearch_suggestions(self):
        c = Client()
        response = c.get('/suggest/', { 'q': 'test'})
        self.assertEqual(response.status_code, 200)

    def test_opensearch_suggest_no_q(self):
        c = Client()
        response = c.get('/suggest/')
        self.assertEqual(response.status_code, 200)

class LDAPAuthTestCase(unittest.TestCase):
    '''
    Testing LDAP authentication
    '''
    top = ('dc=org', {'dc': 'org'})
    top2 = ('dc=example,dc=org', {'dc': 'example'})
    people = ('ou=people,dc=example,dc=org', {'ou': 'people'})
    alice = ('uid=alice,ou=people,dc=example,dc=org',
                {   'uid': 'alice',
                    'userPassword': ['alicepw'],
                    'mail': 'alice@example.org',
                    'givenName': 'alice',
                    'sn': 'Smith',
                })
    bob = ('uid=bob,ou=people,dc=example,dc=org',
                {   'uid': 'bob',
                    'userPassword': ['bobpw'],
                })

    # This is the content of our mock LDAP directory. It takes the form
    # {dn: {attr: [value, ...], ...}, ...}.
    directory = dict([top, top2, people, alice])

    @classmethod
    def setUpClass(cls):
        # We only need to create the MockLdap instance once. The content we
        # pass in will be used for all LDAP connections.
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):
        self.mockldap.start()
        self.ldapobj = self.mockldap['ldap://localhost']

    def tearDown(self):
        self.mockldap.stop()
        del self.ldapobj

    def test_login(self):
        c = Client()
        self.assertTrue(c.login(username='alice', password='alicepw'))
        # Logout and try again now that the user exists checking both codepaths
        c.logout()
        self.assertTrue(c.login(username='alice', password='alicepw'))

    def test_bad_login(self):
        c = Client()
        self.assertFalse(c.login(username='alice', password='wrong'))

    def test_bad_ldap_account_login(self):
        c = Client()
        self.assertFalse(c.login(username='bob', password='bobpw'))

    def test_malformed_account(self):
        c = Client()
        self.assertFalse(c.login(username='*', password='bobpw'))
