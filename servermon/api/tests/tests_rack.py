from rest_framework.test import APITestCase
from django.utils import unittest
from django.test.client import Client

from django.core.urlresolvers import reverse
from hwdoc.models import Vendor, RackModel, Rack

import json


class RackUrlsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_rack(self):
        c = Client()
        response = c.get('/api/rack/')
        self.assertEqual(response.status_code, 200)

    def test_rack_reverse_url(self):
        c = Client()
        url = reverse('rack-list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_rack_wrong_url(self):
        c = Client()
        response = c.get('/api/raa/')
        self.assertEqual(response.status_code, 404)

    def test_rack_filter(self):
        c = Client()
        response = c.get('/api/rack/?name=AAAAA')
        self.assertEqual(response.status_code, 200)


class RackAPIEndpointTestCase(APITestCase):

    def setUp(self):
        '''
        Commands run before every test
        '''

        vendor = Vendor.objects.create(name='HP')
        rackmodel = RackModel.objects.create(
            vendor=vendor,
            inrow_ac=False,
            max_mounting_depth=99,
            min_mounting_depth=19,
            height=42,
            width=19
        )
        self.rack = Rack.objects.create(model=rackmodel, name='testrack')
        self.rack2 = Rack.objects.create(model=rackmodel, name='R02')

    def tearDown(self):
        '''
        Commands run after every test
        '''

        RackModel.objects.all().delete()
        Vendor.objects.all().delete()
        Rack.objects.all().delete()

    def test_get_rack_list(self):
        '''
        Make sure the "rack-list" url (/api/rack)
        returns all the previously entered objects

        Description:
        Get all objects from database, query API for all
        objects and test if the serials are the same
        '''

        url = reverse('rack-list')

        response = self.client.get(url, format='json')
        data = json.loads(response.content)

        db = Rack.objects.all()

        dbitems = [item.name for item in db]
        items = [item['name'] for item in data]

        self.assertListEqual(sorted(dbitems), sorted(items))

    def test_get_filter_name(self):
        '''
        Test the GET parameter filtering (on name)
        works by getting a Rack object from DB,
        checking that names are equal
        '''

        rack = Rack.objects.all()[0]

        url = reverse('rack-list')
        url += ('?name=%s' % rack.name)

        response = self.client.get(url, format='json')
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], rack.name)
