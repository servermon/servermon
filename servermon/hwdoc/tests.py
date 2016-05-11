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
Unit tests for hwdoc package
'''

from django import VERSION as DJANGO_VERSION

from django.utils import unittest
from django.test.client import Client
from django.core.management import call_command, CommandError
from django.conf import settings
from django.contrib.auth.models import User, Permission
from hwdoc.models import Vendor, EquipmentModel, Equipment, \
    ServerManagement, Rack, RackPosition, RackModel, RackRow, \
    Datacenter, Storage, Ticket, \
    Email, Phone, Person, Project, Role
from hwdoc.functions import search
from projectwide.functions import get_search_terms

import os


class EquipmentTestCase(unittest.TestCase):
    '''
    A test case for equipment
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''

        self.vendor = Vendor.objects.create(name='HP')
        self.model1 = EquipmentModel.objects.create(vendor=self.vendor, name='DL 385 G7', u=2)
        self.model2 = EquipmentModel.objects.create(vendor=self.vendor, name='DL 380 G7', u=2)
        self.model2 = EquipmentModel.objects.create(vendor=self.vendor, name='PRIMERGY RX200 S5', u=1)
        self.model3 = EquipmentModel.objects.create(vendor=self.vendor, name='DS2600', u=2)
        self.rackmodel = RackModel.objects.create(
            vendor=self.vendor,
            inrow_ac=False,
            max_mounting_depth=99,
            min_mounting_depth=19,
            height=42,
            width=19
        )
        self.dc = Datacenter.objects.create(name='Test DC')
        self.rackrow = RackRow.objects.create(name='testing', dc=self.dc)
        self.rack = Rack.objects.create(model=self.rackmodel, name='testrack')
        self.rack2 = Rack.objects.create(model=self.rackmodel, name='R02')
        RackPosition.objects.create(rack=self.rack, rr=self.rackrow, position=10)
        self.storage = Storage.objects.create(name='Test DCs storage', dc=self.dc)

        self.server1 = Equipment.objects.create(
            model=self.model1,
            serial='G123456',
            rack=self.rack,
            unit=20,
            purpose='Nothing',
        )

        self.server2 = Equipment.objects.create(
            model=self.model2,
            serial='R123457',
            rack=self.rack,
            unit=22,
            purpose='Nothing',
            comments='Nothing',
        )

        self.server3 = Equipment.objects.create(
            model=self.model2,
            serial='R123458',
            rack=self.rack2,
            unit=23,
            purpose='Nothing',
            comments='Nothing',
        )

        self.management = ServerManagement.objects.create(
            equipment=self.server2,
            method='dummy',
            hostname='example.com',
        )
        self.management2 = ServerManagement.objects.create(
            equipment=self.server3,
            method='error',
            hostname='example.org',
        )
        self.ticket1 = Ticket.objects.create(
            name='012345',
            url='http://ticketing.example.com/012345',
            state='open',
        )
        self.ticket2 = Ticket.objects.create(
            name='myticket2',
            url='http://ticketing.example.com/myticket2',
            state='closed',
        )
        self.ticket1.equipment.add(self.server1)
        self.ticket2.equipment.add(self.server1)

    def tearDown(self):
        '''
        Command run after every test
        '''

        Ticket.objects.all().delete()
        ServerManagement.objects.all().delete()
        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        Vendor.objects.all().delete()
        Rack.objects.all().delete()
        RackRow.objects.all().delete()
        Datacenter.objects.all().delete()
        Storage.objects.all().delete()

    # Tests start here
    def test_if_servers_in_same_rack(self):
        self.assertEqual(self.server1.rack, self.server2.rack)

    def test_rack_empty_units(self):
        self.assertIsInstance(self.rack.get_empty_units(), set)

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
        self.assertTrue(self.management.add_user())
        self.assertTrue(self.management.remove_user())
        self.assertTrue(self.management.get_all_users())
        self.assertTrue(self.management.firmware_update())

    def test_inexistent_method(self):
        self.assertIsNone(self.management2.power_on())

    def test_pass_change_error(self):
        try:
            self.management.pass_change(**{'change_username': 'me'})
        except RuntimeError:
            pass

    def test_equipment_number(self):
        self.assertEqual(Equipment.objects.all().count(), 3)

    def test_search_empty(self):
        self.assertFalse(search(''))

    def test_search_rack(self):
        self.assertEqual(search(str(self.server1.rack.name)).count(), 2)

    def test_search_all(self):
        self.assertEqual(search('ALL_EQS').count(), 3)

    def test_search_rack_heuristic(self):
        self.assertEqual(search('%sU%s' % (self.server3.rack.name, self.server3.unit)).count(), 1)

    def test_search_serial(self):
        self.assertEqual(search(self.server1.serial)[0].serial, self.server1.serial)
        self.assertEqual(search(self.server2.serial)[0].serial, self.server2.serial)

    def test_free_text_search(self):
        text = u'''
        This is a text that is not going to make any sense apart from containing
        a hostname for a server (aka example.com) and a rackunit aka R10U22
        '''

        tokens = get_search_terms(text)
        self.assertNotEqual(len(tokens), 0)

    def test_assess_ticket_count(self):
        self.assertEqual(Ticket.objects.count(), self.server1.ticket_set.all().count())

    def test_ticket_states(self):
        self.assertFalse(self.ticket1.closed())
        self.assertTrue(self.ticket2.closed())

    def test_unicode(self):
        self.assertIsInstance(str(self.ticket1), str)
        self.assertIsInstance(str(self.management), str)


class AllocationTestCase(unittest.TestCase):
    '''
    A test case for equipment
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''
        self.email1 = Email.objects.create(email="test@example.com")
        self.phone1 = Phone.objects.create(number="5555555555")
        self.person1 = Person.objects.create(name='test', surname='test')
        self.person1.emails.add(self.email1)
        self.person1.phones.add(self.phone1)
        self.person1.save()
        self.project1 = Project.objects.create(name='test project')
        self.role1 = Role.objects.create(
            role='technical contact', project=self.project1, person=self.person1)

    def tearDown(self):
        '''
        Command run after every test
        '''

        Email.objects.all().delete()
        Phone.objects.all().delete()
        Person.objects.all().delete()
        Project.objects.all().delete()
        Role.objects.all().delete()

    def test_print_check(self):
        self.assertIsInstance(str(self.email1), str)
        self.assertIsInstance(str(self.phone1), str)
        self.assertIsInstance(str(self.person1), str)
        self.assertIsInstance(str(self.project1), str)
        self.assertIsInstance(str(self.role1), str)


class ViewsTestCase(unittest.TestCase):
    '''
    Testing views class
    '''

    def setUp(self):
        '''
        Command run before every test
        '''

        self.vendor = Vendor.objects.create(name='HP')
        self.model = EquipmentModel.objects.create(vendor=self.vendor, name='DL 385 G7', u=2)
        self.rackmodel = RackModel.objects.create(
            vendor=self.vendor, inrow_ac=False, max_mounting_depth=99,
            min_mounting_depth=19, height=42, width=19)
        self.rack = Rack.objects.create(model=self.rackmodel, name='testrack')
        self.project = Project.objects.create(name='project')

        self.server = Equipment.objects.create(
            model=self.model, serial='dontcare', rack=self.rack,
            unit='2', purpose='Nothing', allocation=self.project,)

        self.dc = Datacenter.objects.create(name='Test DC')
        self.rackrow = RackRow.objects.create(name='1st rackrow', dc=self.dc)
        RackPosition.objects.create(rack=self.rack, rr=self.rackrow, position=10)
        self.racknotinrow = Rack.objects.create(model=self.rackmodel, name='racknotinrow')
        self.storage = Storage.objects.create(name='Test DCs storage', dc=self.dc)

        self.server_unallocated = Equipment.objects.create(
            model=self.model, serial='unallocated', rack=self.rack,
            unit='2', purpose='Nothing',)
        self.server_commented = Equipment.objects.create(
            model=self.model, serial='commented', rack=self.rack, unit='2',
            purpose='Nothing', comments='blah blah',)
        self.server_ticketed = Equipment.objects.create(
            model=self.model, serial='ticketed', rack=self.rack, unit='2',
            purpose='Nothing',)
        self.server_unracked = Equipment.objects.create(
            model=self.model, serial='unracked', purpose='Nothing',)
        self.ticket = Ticket.objects.create(
            name='myticket', url='http://example.com/myticket', state='open')
        self.server_ticketed.ticket_set.add(self.ticket)

    def tearDown(self):
        '''
        Command run after every test
        '''
        Ticket.objects.all().delete()
        ServerManagement.objects.all().delete()
        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        Vendor.objects.all().delete()
        Rack.objects.all().delete()
        RackRow.objects.all().delete()
        Datacenter.objects.all().delete()
        Storage.objects.all().delete()

    def test_index(self):
        c = Client()
        response = c.get('/hwdoc/')
        self.assertEqual(response.status_code, 200)

    def test_equipment(self):
        c = Client()
        response = c.get('/hwdoc/equipment/%s/' % self.server.pk)
        self.assertEqual(response.status_code, 200)
        response = c.get('/hwdoc/equipment/%s/' % self.server.serial)
        self.assertEqual(response.status_code, 200)

    def test_inexistent_equipment(self):
        c = Client()
        response = c.get('/hwdoc/equipment/%s/' % 20000)
        self.assertEqual(response.status_code, 404)
        response = c.get('/hwdoc/equipment/%s/' % 'INEXISTENT_SERIAL')
        self.assertEqual(response.status_code, 404)

    def test_equipment_unracked(self):
        c = Client()
        response = c.get('/hwdoc/equipment/%s/' % self.server_unracked.pk)
        self.assertEqual(response.status_code, 200)

    def test_project(self):
        c = Client()
        response = c.get('/hwdoc/project/%s/' % self.project.pk)
        self.assertEqual(response.status_code, 200)

    def test_unallocated_equipment(self):
        c = Client()
        response = c.get('/hwdoc/equipment/unallocated')
        self.assertEqual(response.status_code, 200)

    def test_commented_equipment(self):
        c = Client()
        response = c.get('/hwdoc/equipment/commented')
        self.assertEqual(response.status_code, 200)

    def test_ticketed_equipment(self):
        c = Client()
        response = c.get('/hwdoc/equipment/ticketed')
        self.assertEqual(response.status_code, 200)

    def test_unracked_equipment(self):
        c = Client()
        response = c.get('/hwdoc/equipment/unracked')
        self.assertEqual(response.status_code, 200)

    def test_datacenter(self):
        c = Client()
        response = c.get('/hwdoc/datacenter/%s/' % self.dc.pk)
        self.assertEqual(response.status_code, 200)

    def test_storage(self):
        c = Client()
        response = c.get('/hwdoc/storage/%s/' % self.storage.pk)
        self.assertEqual(response.status_code, 200)

    def test_rackrow(self):
        c = Client()
        response = c.get('/hwdoc/rackrow/%s/' % self.rackrow.pk)
        self.assertEqual(response.status_code, 200)

    def test_rack_in_row(self):
        c = Client()
        response = c.get('/hwdoc/rack/%s/' % self.rack.pk)
        self.assertEqual(response.status_code, 200)

    def test_rack_not_in_row(self):
        c = Client()
        response = c.get('/hwdoc/rack/%s/' % self.racknotinrow.pk)
        self.assertEqual(response.status_code, 200)

    def test_subnav(self):
        c = Client()
        response = c.get('/hwdoc/subnav/%s/' % 'datacenters',
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

    def test_subnav_bad_arg(self):
        c = Client()
        response = c.get('/hwdoc/subnav/%s/' % 'inexistent',
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_subnav_no_ajax(self):
        c = Client()
        response = c.get('/hwdoc/subnav/%s/' % 'datacenters')
        self.assertEqual(response.status_code, 400)

    def test_flotdata(self):
        c = Client()
        response = c.get('/hwdoc/flotdata/%s/' % 'datacenters',
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

    def test_flotdat_bad_arg(self):
        c = Client()
        response = c.get('/hwdoc/flotdata/%s/' % 'inexistent',
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_flotdata_noajax(self):
        c = Client()
        response = c.get('/hwdoc/flotdata/%s/' % 'datacenters')
        self.assertEqual(response.status_code, 400)


class CommandsTestCase(unittest.TestCase):
    '''
    A test case for django management commands
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''
        settings.TICKETING_SYSTEM = 'dummy'

        self.vendor = Vendor.objects.create(name='HP')
        self.model1 = EquipmentModel.objects.create(vendor=self.vendor, name='DL385 G7', u=2)
        self.model2 = EquipmentModel.objects.create(vendor=self.vendor, name='DL380 G7', u=2)
        self.model2 = EquipmentModel.objects.create(vendor=self.vendor, name='PRIMERGY RX200 S5', u=1)
        self.model3 = EquipmentModel.objects.create(vendor=self.vendor, name='DS2600', u=2)
        self.rackmodel = RackModel.objects.create(
            vendor=self.vendor, inrow_ac=False, max_mounting_depth=99, min_mounting_depth=19,
            height=42, width=19)
        self.dc = Datacenter.objects.create(name='Test DC')
        self.rackrow = RackRow.objects.create(name='testing', dc=self.dc)
        self.rack = Rack.objects.create(model=self.rackmodel, name='testrack')
        RackPosition.objects.create(rack=self.rack, rr=self.rackrow, position=10)

        self.server1 = Equipment.objects.create(
            model=self.model1, serial='G123456', rack=self.rack,
            unit='20', purpose='Nothing',)

        self.server2 = Equipment.objects.create(
            model=self.model2, serial='R123457', rack=self.rack, unit='22',
            purpose='Nothing', comments='http://ticketing.example.com/012345',)

        self.management = ServerManagement.objects.create(
            equipment=self.server2, method='dummy', hostname='example.com',)

    def tearDown(self):
        '''
        Command run after every test
        '''

        ServerManagement.objects.all().delete()
        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        Vendor.objects.all().delete()
        # Also clear tickets that may be created by commands
        Ticket.objects.all().delete()

    # Tests start here
    def test_bmc_commands(self):
        call_command('hwdoc_bmc_reset', self.server2.serial, verbosity=0)
        call_command('hwdoc_add_user', self.server2.serial, verbosity=0)
        call_command('hwdoc_bmc_factory_defaults', self.server2.serial, verbosity=0)
        call_command('hwdoc_bmc_reset', self.server2.serial, verbosity=0)
        call_command('hwdoc_boot_order', self.server2.serial, verbosity=0)
        call_command('hwdoc_get_all_users', self.server2.serial, verbosity=0)
        call_command('hwdoc_license', self.server2.serial, verbosity=0)
        call_command('hwdoc_power_cycle', self.server2.serial, verbosity=0)
        call_command('hwdoc_remove_user', self.server2.serial, verbosity=0)
        call_command('hwdoc_reset', self.server2.serial, verbosity=0)
        call_command('hwdoc_set_ldap_settings', self.server2.serial,
                     contexts='ou=example,ou=com:ou=example,ou=org',
                     groupnames='group1:group2',
                     groupprivs='priv1:priv2',
                     groupsids='S-123:S-124',
                     verbosity=0)
        call_command('hwdoc_set_settings', self.server2.serial, verbosity=0)
        call_command('hwdoc_shutdown', self.server2.serial, verbosity=0)
        call_command('hwdoc_shutdown', self.server2.serial, force=True, verbosity=0)
        call_command('hwdoc_startup', self.server2.serial, verbosity=0)
        # Actually check with verbosity=1
        call_command('hwdoc_startup', self.server2.serial, verbosity=1)

    def test_bmc_command_pass_change(self):
        call_command('hwdoc_pass_change', self.server2.serial,
                     change_username='username',
                     newpass='password',
                     verbosity=0)

    def test_bmc_commands_bad_call(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_startup')
        try:
            call_command('hwdoc_startup', verbosity=0)
        except CommandError:
            pass

    def test_bmc_commands_no_result(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_startup')
        try:
            call_command('hwdoc_startup', 'INEXISTENT_EQUIPMENT', verbosity=0)
        except CommandError:
            pass

    def test_bmc_commands_no_servermanagement(self):
        call_command('hwdoc_startup', self.server1.serial, verbosity=0)

    def test_importequipment(self):
        filename = 'test_importequiment.csv'
        f = open(filename, 'w')
        f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
            '1', 'VMC01', 'A123456', 'test1.example.com', 'password', self.rack.name,
            '10', 'PDA', 'PDB', 'AA:BB:CC:DD:EE:FA'))
        f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
            '2', 'SC0-DS1', 'B123456', 'test2.example.com', 'password', self.rack.name,
            '11', 'PDA', 'PDB', 'AA:BB:CC:DD:EE:FB'))
        f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
            '3', 'HN01', 'C123456', 'test3.example.com', 'password', self.rack.name,
            '12', 'PDA', 'PDB', 'AA:BB:CC:DD:EE:FC'))
        f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
            '4', 'DS01', 'D123456', 'test4.example.com', 'password', self.rack.name,
            '13', 'PDA', 'PDB', 'AA:BB:CC:DD:EE:FD'))
        f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
            '5', 'SC01', 'E123456', 'test5.example.com', 'password', self.rack.name,
            '14', 'PDA', 'PDB', 'AA:BB:CC:DD:EE:FE'))
        f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
            '6', 'EC01', 'F123456', 'test6.example.com', 'password', self.rack.name,
            '15', 'PDA', 'PDB', 'AA:BB:CC:DD:EE:FF'))
        f.close()
        call_command('hwdoc_importequipment', filename, verbosity=0)
        os.remove(filename)

    def test_importequipment_nofile_specified(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_importequipment')
        try:
            call_command('hwdoc_importequipment', verbosity=0)
        except CommandError:
            pass

    def test_importequipment_nonexistent_file(self):
        filename = 'test_importequiment.csv'
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_importequipment')
        try:
            call_command('hwdoc_importequipment', filename, verbosity=0)
        except CommandError:
            pass

    def test_importequipmentlicenses(self):
        filename = 'test_importequipmentlicenses.csv'
        f = open(filename, 'w')
        f.write('%s,%s,%s' % ('foo', 'mylicense', self.server2.serial))
        f.close()
        call_command('hwdoc_importequipmentlicenses', filename, verbosity=0)
        os.remove(filename)

    def test_importequipmentlicenses_nonexistent_file(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_importequipmentlicenses')
        try:
            call_command('hwdoc_importequipmentlicenses')
        except CommandError:
            pass

    def test_bmc_firmware_update(self):
        filename = 'firmware'
        f = open(filename, 'w')
        f.write('THIS IS A FIRMWARE. Yeah...it is')
        f.close()
        call_command('hwdoc_firmware_update',
                     self.server2.serial,
                     firmware_location='firmware',
                     verbosity=0)
        os.remove(filename)

    def test_bmc_firmware_update_nonexistent_file(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_firmware_update')
        try:
            call_command('hwdoc_firmware_update',
                         self.server2.serial,
                         firmware_location='firmware',
                         verbosity=0)
        except CommandError:
            pass

    def test_bmc_firmware_update_no_specified_file(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_firmware_update')
        try:
            call_command('hwdoc_firmware_update', self.server2.serial, verbosity=0)
        except CommandError:
            pass

    def test_bmc_pass_change_no_username(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_pass_change')
        try:
            call_command('hwdoc_pass_change',
                         self.server2.serial,
                         newpass='password',
                         verbosity=0)
        except CommandError:
            pass

    def test_bmc_pass_change_no_password(self):
        if DJANGO_VERSION[:2] < (1, 5):
            from compat import monkey_patch_command_execute
            monkey_patch_command_execute('hwdoc_pass_change')
        try:
            call_command('hwdoc_pass_change',
                         self.server2.serial,
                         change_username='username',
                         verbosity=0)
        except CommandError:
            pass

    def test_populate_tickets(self):
        settings.TICKETING_SYSTEM = 'dummy'
        call_command('hwdoc_populate_tickets', self.server1.serial, verbosity=0)

    def test_populate_tickets_comments(self):
        settings.TICKETING_SYSTEM = 'comments'
        settings.COMMENTS_TICKETING_URL = 'http://ticketing.example.com/'
        call_command('hwdoc_populate_tickets', self.server2.serial, verbosity=0)

    def test_populate_tickets_inexistent_system(self):
        settings.TICKETING_SYSTEM = 'nosuchthing'
        call_command('hwdoc_populate_tickets', self.server1.serial, verbosity=0)


class AdminViewsTestCase(EquipmentTestCase):
    '''
    Testing admin views class
    '''

    def setUp(self):
        '''
        Command run before every test
        '''
        # Let's call our parent so we can benefit from it's fields
        super(AdminViewsTestCase, self).setUp()

        self.u1 = User.objects.create(
            username='test1', email='test1@example.com', is_staff=True, is_superuser=True)
        self.u2 = User.objects.create(
            username='test2', email='test2@example.com', is_staff=True, is_superuser=False)
        self.u3 = User.objects.create(
            username='test3', email='test3@example.com', is_staff=True, is_superuser=False)
        self.u4 = User.objects.create(
            username='test4', email='test4@example.com', is_staff=True, is_superuser=False)
        self.p_comment = Permission.objects.get(codename='can_change_comment')
        self.p_c_eq = Permission.objects.get(codename='change_equipment')
        self.u2.user_permissions.add(self.p_comment)
        self.u4.user_permissions.add(self.p_c_eq)
        self.u1.set_password('test')
        self.u2.set_password('test')
        self.u3.set_password('test')
        self.u4.set_password('test')
        self.u1.save()
        self.u2.save()
        self.u3.save()
        self.u4.save()
        self.c1 = Client()
        self.c2 = Client()
        self.c3 = Client()
        self.c4 = Client()
        self.assertTrue(self.c1.login(username='test1', password='test'))
        self.assertTrue(self.c2.login(username='test2', password='test'))
        self.assertTrue(self.c3.login(username='test3', password='test'))
        self.assertTrue(self.c4.login(username='test4', password='test'))

    def tearDown(self):
        '''
        Command run after every test
        '''
        self.c1.logout()
        self.c2.logout()
        self.c3.logout()
        self.c4.logout()
        User.objects.all().delete()
        super(AdminViewsTestCase, self).tearDown()

    def test_admin_datacenter(self):
        response = self.c1.get('/admin/hwdoc/datacenter/')
        self.assertEqual(response.status_code, 200)
        response = self.c3.get('/admin/hwdoc/datacenter/')
        self.assertEqual(response.status_code, 403)

    def test_admin_email(self):
        response = self.c1.get('/admin/hwdoc/email/')
        self.assertEqual(response.status_code, 200)

    def test_admin_equipmentmodel(self):
        response = self.c1.get('/admin/hwdoc/equipmentmodel/')
        self.assertEqual(response.status_code, 200)

    def test_admin_equipment(self):
        response = self.c1.get('/admin/hwdoc/equipment/')
        self.assertEqual(response.status_code, 200)
        response = self.c2.get('/admin/hwdoc/equipment/')
        self.assertEqual(response.status_code, 200)
        response = self.c3.get('/admin/hwdoc/equipment/')
        self.assertEqual(response.status_code, 403)
        response = self.c4.get('/admin/hwdoc/equipment/')
        self.assertEqual(response.status_code, 200)

    def test_admin_equipment1(self):
        response = self.c1.get('/admin/hwdoc/equipment/%s/' % self.server1.id)
        self.assertEqual(response.status_code, 200)
        response = self.c2.get('/admin/hwdoc/equipment/%s/' % self.server1.id)
        self.assertEqual(response.status_code, 200)
        response = self.c3.get('/admin/hwdoc/equipment/%s/' % self.server1.id)
        self.assertEqual(response.status_code, 403)
        response = self.c4.get('/admin/hwdoc/equipment/%s/' % self.server1.id)
        self.assertEqual(response.status_code, 200)

    def test_admin_person(self):
        response = self.c1.get('/admin/hwdoc/person/')
        self.assertEqual(response.status_code, 200)

    def test_admin_phone(self):
        response = self.c1.get('/admin/hwdoc/phone/')
        self.assertEqual(response.status_code, 200)

    def test_admin_project(self):
        response = self.c1.get('/admin/hwdoc/project/')
        self.assertEqual(response.status_code, 200)

    def test_admin_rackmodel(self):
        response = self.c1.get('/admin/hwdoc/rackmodel/')
        self.assertEqual(response.status_code, 200)

    def test_admin_rackrow(self):
        response = self.c1.get('/admin/hwdoc/rackrow/')
        self.assertEqual(response.status_code, 200)

    def test_admin_rack(self):
        response = self.c1.get('/admin/hwdoc/rack/')
        self.assertEqual(response.status_code, 200)

    def test_admin_ticket(self):
        response = self.c1.get('/admin/hwdoc/ticket/')
        self.assertEqual(response.status_code, 200)

    def test_admin_vendor(self):
        response = self.c1.get('/admin/hwdoc/vendor/')
        self.assertEqual(response.status_code, 200)


class MigrationsTestCase(unittest.TestCase):
    '''
    A test case for migration testing
    '''

    def setUp(self):
        # Do a fake migration first to update the migration history.
        call_command('migrate', 'hwdoc',
                     fake=True, verbosity=0, no_initial_data=True)
        # Then rollback to the start
        call_command('migrate', 'hwdoc', '0001_initial',
                     verbosity=0, no_initial_data=True)

    def tearDown(self):
        # We do need to tidy up and take the database to its final
        # state so that we don't get errors when the final truncating
        # happens.
        call_command('migrate', 'hwdoc',
                     verbosity=0, no_initial_data=True)

    def test_migrate_full_forwards(self):
        call_command('migrate', 'hwdoc',
                     verbosity=0, no_initial_data=True)

    def test_migrate_full_backwards(self):
        call_command('migrate', 'hwdoc', '0001_initial',
                     verbosity=0, no_initial_data=True)
