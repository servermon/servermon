from rest_framework.test import APITestCase
from django.utils import unittest
from django.test.client import Client

from django.core.urlresolvers import reverse
from hwdoc.models import (
    Vendor, Equipment, EquipmentModel, RackModel, Datacenter, Rack, RackRow,
    Storage, RackPosition, Project, ServerManagement
)

from keyvalue.models import Key, KeyValue
from django.contrib.contenttypes.models import ContentType

from api.serializers import EquipmentSerializer, EquipmentModelSerializer

import json


class EquipmentUrlsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_equipment(self):
        c = Client()
        response = c.get('/api/equipment/')
        self.assertEqual(response.status_code, 200)

    def test_equipment_reverse_url(self):
        c = Client()
        url = reverse('equipment-list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_equipment_wrong_url(self):
        c = Client()
        response = c.get('/api/equipme/')
        self.assertEqual(response.status_code, 404)

    def test_equipment_filter(self):
        c = Client()
        response = c.get('/api/equipment/?serial=AAAAA')
        self.assertEqual(response.status_code, 200)


class EquipmentAPIEndpointTestCase(APITestCase):

    def setUp(self):
        '''
        Commands run before every test
        '''

        self.vendor = Vendor.objects.create(name='HP')
        self.model1 = EquipmentModel.objects.create(vendor=self.vendor, name='DL 385 G7', u=2)
        self.model2 = EquipmentModel.objects.create(vendor=self.vendor, name='DL 380 G7', u=2)
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

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        RackModel.objects.all().delete()
        Datacenter.objects.all().delete()
        Vendor.objects.all().delete()
        Rack.objects.all().delete()
        RackRow.objects.all().delete()
        RackPosition.objects.all().delete()
        Storage.objects.all().delete()

    def test_get_equipment_list(self):
        '''
        Make sure the "equipment-list" url (/api/equipment)
        returns all the previously entered objects

        Description:
        Get all objects from database, query API for all
        objects and test if the serials are the same
        '''

        url = reverse('equipment-list')

        response = self.client.get(url, format='json')
        data = json.loads(response.content)

        db = Equipment.objects.all()

        dbitems = [item.serial for item in db]
        items = [item['serial'] for item in data]

        self.assertListEqual(sorted(dbitems), sorted(items))

    def test_get_filter_serial(self):
        '''
        Test the GET parameter filtering (on serial number)
        works by getting an Equipment object from DB,
        checking that serial numbers are equal
        '''

        equipment = Equipment.objects.all()[0]

        url = reverse('equipment-list')
        url += ('?serial=%s' % equipment.serial)

        response = self.client.get(url, format='json')
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['serial'], equipment.serial)


class EquipmentSerializerUnitTestCase(APITestCase):

    def setUp(self):
        '''
        Commands run before every test
        '''

        vendor = Vendor.objects.create(name='HP')
        model1 = EquipmentModel.objects.create(vendor=vendor, name='DL 385 G7', u=2)
        model2 = EquipmentModel.objects.create(vendor=vendor, name='DL 380 G7', u=2)
        rackmodel = RackModel.objects.create(
            vendor=vendor,
            inrow_ac=False,
            max_mounting_depth=99,
            min_mounting_depth=19,
            height=42,
            width=19
        )
        dc = Datacenter.objects.create(name='Test DC')
        rackrow = RackRow.objects.create(name='testing', dc=dc)
        rack = Rack.objects.create(model=rackmodel, name='testrack')
        rack2 = Rack.objects.create(model=rackmodel, name='R02')
        RackPosition.objects.create(rack=rack, rr=rackrow, position=10)
        Storage.objects.create(name='Test DCs storage', dc=dc)
        project = Project.objects.create(name='TestProject')

        server1 = Equipment.objects.create(
            model=model1,
            serial='G123456',
            rack=rack,
            unit=20,
            purpose='Nothing',
            allocation=project
        )
        Equipment.objects.create(
            model=model2,
            serial='R123457',
            rack=rack2,
            unit=22,
            purpose='Nothing',
            comments='Nothing',
        )

        Equipment.objects.create(
            model=model2,
            serial='C1234567',
            rack=None,
            unit=22,
            purpose='Nothing',
            comments='Nothing',
        )

        ServerManagement.objects.create(
            equipment=server1,
            method='dummy',
            hostname='example.com',
            mac='ff:ff:ff:ff:ff:ff',
        )

        key = Key(name='key')
        key.save()
        KeyValue.objects.create(
            key=key,
            value='value',
            owner_content_type=ContentType.objects.get_for_model(Equipment),
            owner_object_id=server1.id,
        )

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        RackModel.objects.all().delete()
        Datacenter.objects.all().delete()
        Vendor.objects.all().delete()
        Rack.objects.all().delete()
        RackRow.objects.all().delete()
        RackPosition.objects.all().delete()
        Storage.objects.all().delete()
        Project.objects.all().delete()
        ServerManagement.objects.all().delete()
        Key.objects.all().delete()
        KeyValue.objects.all().delete()

    """
    Unit tests for get_allocation
    """

    def test_get_allocation_existent(self):

        equipment = Equipment.objects.get(serial='G123456')
        allocation = equipment.allocation
        serializer = EquipmentSerializer()
        self.assertEqual(allocation, serializer.get_allocation(equipment))

    def test_get_allocation_nonexistent(self):

        equipment = Equipment.objects.get(serial='R123457')
        serializer = EquipmentSerializer()
        self.assertEqual(None, serializer.get_allocation(equipment))

    def test_get_allocation_none(self):

        serializer = EquipmentSerializer()
        self.assertEqual(None, serializer.get_allocation(None))

    """
    Unit tests for get_ipmi
    """

    def test_get_ipmi_existent(self):

        equipment = Equipment.objects.get(serial='G123456')
        serializer = EquipmentSerializer()
        ipmi = {
            'IPMI Hostname': equipment.servermanagement.hostname,
            'IPMI Mac': equipment.servermanagement.mac
        }
        self.assertEqual(ipmi, serializer.get_ipmi(equipment))

    def test_get_ipmi_nonexistent(self):

        equipment = Equipment.objects.get(serial='R123457')
        serializer = EquipmentSerializer()
        ipmi = {
            'IPMI Hostname': None,
            'IPMI Mac': None
        }
        self.assertEqual(ipmi, serializer.get_ipmi(equipment))

    def test_get_ipmi_none(self):

        serializer = EquipmentSerializer()
        ipmi = {
            'IPMI Hostname': None,
            'IPMI Mac': None
        }
        self.assertEqual(ipmi, serializer.get_ipmi(None))

    """
    Unit tests for get_rack
    """

    def test_get_rack_existent(self):

        equipment = Equipment.objects.get(serial='G123456')
        serializer = EquipmentSerializer()
        rack = {
            'rack': equipment.rack.name,
            'rackunit': equipment.unit
        }
        self.assertEqual(rack, serializer.get_rack(equipment))

    def test_get_rack_nonexistent(self):

        equipment = Equipment.objects.get(serial='C1234567')
        serializer = EquipmentSerializer()
        rack = {
            'rack': None,
            'rackunit': None
        }
        self.assertEqual(rack, serializer.get_rack(equipment))

    def test_get_rack_none(self):

        serializer = EquipmentSerializer()
        rack = {
            'rack': None,
            'rackunit': None
        }
        self.assertEqual(rack, serializer.get_rack(None))

    """
    Unit tests for get_attrs
    """

    def test_get_attrs_existent(self):

        equipment = Equipment.objects.get(serial='G123456')
        serializer = EquipmentSerializer()
        attrs = {
            'key': 'value'
        }
        self.assertEqual(attrs, serializer.get_attrs(equipment))

    def test_get_attrs_nonexistent(self):

        equipment = Equipment.objects.get(serial='C1234567')
        serializer = EquipmentSerializer()
        attrs = {}
        self.assertEqual(attrs, serializer.get_attrs(equipment))

    def test_get_attrs_none(self):

        serializer = EquipmentSerializer()
        attrs = {}
        self.assertEqual(attrs, serializer.get_attrs(None))

    """
    Unit tests for get_dc_name
    """

    def test_get_dc_name_existent(self):

        equipment = Equipment.objects.get(serial='G123456')
        serializer = EquipmentSerializer()
        name = equipment.dc.name
        self.assertEqual(name, serializer.get_dc_name(equipment))

    def test_get_dc_name_nonexistent(self):

        equipment = Equipment.objects.get(serial='C1234567')
        serializer = EquipmentSerializer()
        name = None
        self.assertEqual(name, serializer.get_dc_name(equipment))

    def test_get_dc_name_none(self):

        serializer = EquipmentSerializer()
        name = None
        self.assertEqual(name, serializer.get_dc_name(None))

    """
    Unit tests for get_vendor_name
    """

    def test_get_vendor_existent(self):

        eq_model = EquipmentModel.objects.get(name='DL 380 G7')
        serializer = EquipmentModelSerializer()
        vendor = eq_model.vendor
        self.assertEqual(vendor, serializer.get_vendor(eq_model))
