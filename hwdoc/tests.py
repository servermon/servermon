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

import unittest
from hwdoc.models import Vendor,Model,Equipment, ServerManagement
from hwdoc.functions import search

class EquipmentTestCase(unittest.TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(name='HP')
        self.model1 = Model.objects.create(vendor=self.vendor, name='DL 385 G7', u=2)
        self.model2 = Model.objects.create(vendor=self.vendor, name='DL 380 G7', u=2)

        self.server1 = Equipment.objects.create(
                                model = self.model1,
                                serial = '123456',
                                rack = '10',
                                unit = '20',
                                purpose = 'Nothing',
                            )

        self.server2 = Equipment.objects.create(
                                model = self.model2,
                                serial = '123457',
                                rack = '10',
                                unit = '22',
                                purpose = 'Nothing',
                            )

        self.management = ServerManagement.objects.create (
                            equipment = self.server2,
                            method = 'dummy',
                            hostname = 'example.com',
                            )

    def tearDown(self):
        Equipment.objects.all().delete()
        Model.objects.all().delete()
        Vendor.objects.all().delete()

    # Tests start here
    def test_if_servers_in_same_rack(self):
        self.assertEqual(self.server1.rack, self.server2.rack)

    def test_dummy_management_fuctions(self):
        self.assertTrue(self.management.power_on())
        self.assertTrue(self.management.power_off())
        self.assertTrue(self.management.power_cycle())
        self.assertTrue(self.management.power_reset())
        self.assertTrue(self.management.power_off_acpi())
        self.assertTrue(self.management.pass_change(**{'change_username': 'me', 'newpass': 'us'}))
        self.assertTrue(self.management.set_settings())
        self.assertTrue(self.management.set_ldap_settings())
        self.assertTrue(self.management.boot_order())
        self.assertTrue(self.management.license_set())
        self.assertTrue(self.management.bmc_reset())
        self.assertTrue(self.management.bmc_factory_defaults())

    def test_equipment_number(self):
        self.assertEqual(Equipment.objects.all().count(), 2)

    def test_search_empty(self):
        self.assertFalse(search(''))

    def test_search_rack(self):
        self.assertEqual(search(self.server1.rack).count(), 2)

    def test_search_serial(self):
        self.assertEqual(search(self.server1.serial)[0].serial, self.server1.serial)

