from rest_framework.test import APITestCase
from django.utils import unittest
from django.test.client import Client

from django.core.urlresolvers import reverse
from hwdoc.models import Project

import json


class ProjectUrlsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_rack(self):
        c = Client()
        response = c.get('/api/project/')
        self.assertEqual(response.status_code, 200)

    def test_rack_reverse_url(self):
        c = Client()
        url = reverse('project-list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_rack_wrong_url(self):
        c = Client()
        response = c.get('/api/proje/')
        self.assertEqual(response.status_code, 404)


class ProjectAPIEndpointTestCase(APITestCase):

    def setUp(self):
        '''
        Commands run before every test
        '''

        Project.objects.create(name='TestProject')
        Project.objects.create(name='TestProject2')

    def tearDown(self):
        '''
        Commands run after every test
        '''

        Project.objects.all().delete()

    def test_get_project_list(self):
        '''
        Make sure the "project-list" url (/api/project)
        returns all the previously entered objects

        Description:
        Get all objects from database, query API for all
        objects and test if the serials are the same
        '''

        url = reverse('project-list')

        response = self.client.get(url, format='json')
        data = json.loads(response.content)

        db = Project.objects.all()

        dbitems = [item.name for item in db]
        items = [item['name'] for item in data]

        self.assertListEqual(sorted(dbitems), sorted(items))
