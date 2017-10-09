from rest_framework.test import APITestCase
from django.utils import unittest
from django.test.client import Client

from django.core.urlresolvers import reverse
from hwdoc.models import (
    Vendor, Equipment, EquipmentModel, RackModel, Rack, ServerManagement,
    Project
)

import json


class ServerManagementUrlsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_servermanagement(self):
        c = Client()
        response = c.get('/api/servermanagement/')
        self.assertEqual(response.status_code, 200)

    def test_servermanagement_reverse_url(self):
        c = Client()
        url = reverse('servermanagement-list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_servermanagement_wrong_url(self):
        c = Client()
        response = c.get('/api/serverment/')
        self.assertEqual(response.status_code, 404)

    def test_servermanagement_filter(self):
        c = Client()
        response = c.get('/api/servermanagement/?hostname=AAAAA')
        self.assertEqual(response.status_code, 200)


class ServerManagementAPIEndpointTestCase(APITestCase):

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
        rack = Rack.objects.create(model=rackmodel, name='testrack')
        rack2 = Rack.objects.create(model=rackmodel, name='R02')
        project = Project.objects.create(name='TestProject')

        server1 = Equipment.objects.create(
            model=model1,
            serial='G123456',
            rack=rack,
            unit=20,
            purpose='Nothing',
            allocation=project
        )
        server2 = Equipment.objects.create(
            model=model2,
            serial='R123457',
            rack=rack2,
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

        ServerManagement.objects.create(
            equipment=server2,
            method='dummy',
            hostname='example23.com',
            mac='fe:fe:ef:fe:ef:fe',
        )

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        Vendor.objects.all().delete()
        Rack.objects.all().delete()
        Project.objects.all().delete()
        ServerManagement.objects.all().delete()

    def test_get_servermanagement_list(self):
        '''
        Make sure the "servermanagement-list" url (/api/servermanagement)
        returns all the previously entered objects

        Description:
        Get all objects from database, query API for all
        objects and test if the serials are the same
        '''

        url = reverse('servermanagement-list')

        response = self.client.get(url, format='json')
        data = json.loads(response.content)

        db = ServerManagement.objects.all()

        dbitems = [item.hostname for item in db]
        items = [item['hostname'] for item in data]

        self.assertListEqual(sorted(dbitems), sorted(items))

    def test_get_filter_name(self):
        '''
        Test the GET parameter filtering (on hostname)
        works by getting a ServerManagement object from DB,
        checking that hostnames are equal
        '''

        servermanagement = ServerManagement.objects.all()[0]

        url = reverse('servermanagement-list')
        url += ('?hostname=%s' % servermanagement.hostname)

        response = self.client.get(url, format='json')
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['hostname'], servermanagement.hostname)
