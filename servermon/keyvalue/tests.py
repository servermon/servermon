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
Unit tests for keyvalue package
'''

from django.contrib.auth.models import User
from django.test.client import Client
from django.utils import unittest
from keyvalue.models import Key, KeyValue


class KeyTestCase(unittest.TestCase):
    def setUp(self):
        # We need a Model instance as an owner
        self.owner = Key.objects.create(name='Owner')

        # Create 4 Key instances
        self.key1 = Key.objects.create(name='Key1')
        self.key2 = Key.objects.create(name='Key2', description='Key 2')
        self.key3 = Key.objects.create(name='Key3', description='Key 3')
        self.key4 = Key.objects.create(name='Key4', description='Key 4')

        # Create 1 KeyValue instance
        self.keyvalue = KeyValue.objects.create(owner_content_object=self.owner,
                                                key=self.key1, value='Yo')

    def tearDown(self):
        self.keyvalue.delete()
        self.key1.delete()
        self.key2.delete()
        self.key3.delete()
        self.key4.delete()
        self.owner.delete()

    def test_key(self):
        # Do a quick match on the first Key created
        self.assertEqual(self.key1, Key.objects.get(name='Key1'))
        # Test name field on Key
        self.assertEqual(self.key1.name, 'Key1')
        # Test __unicode__ method on Key without description
        self.assertEqual(str(self.key1), 'Key1')
        # Test __unicode__ method on Key with description
        self.assertEqual(str(self.key2), 'Key2 - Key 2')

    def test_keyvalue(self):
        self.assertEqual(self.keyvalue.name, 'Key1')
        self.assertEqual(self.keyvalue.verbose_name, 'Key1')
        self.assertEqual(self.keyvalue.description, '')
        self.assertEqual(self.keyvalue.value, 'Yo')
        self.assertEqual(self.keyvalue.owner, self.owner)
        # Test __unicode__ method on KeyValue
        self.assertEqual(str(self.keyvalue), 'Key1 = Yo on Owner')


class AdminViewsTestCase(unittest.TestCase):
    '''
    Testing admin views class
    '''

    def setUp(self):
        '''
        Command run before every test
        '''
        self.u1 = User.objects.create(username='test1', email='test1@example.com',
                                      is_staff=True, is_superuser=True)
        self.u1.set_password('test')
        self.u1.save()
        self.c1 = Client()
        self.assertTrue(self.c1.login(username='test1', password='test'))
        self.key1 = Key.objects.create(name='Key1')

    def tearDown(self):
        '''
        Command run after every test
        '''
        self.key1.delete()
        self.c1.logout()
        User.objects.all().delete()

    def test_admin_keyvalue(self):
        response = self.c1.get('/admin/keyvalue/key/')
        self.assertEqual(response.status_code, 200)

    def test_admin_keyvalue1(self):
        response = self.c1.get('/admin/keyvalue/key/%s/' % self.key1.id)
        self.assertEqual(response.status_code, 200)
