from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class TestList(APITestCase):
    # To test the list rest-api

    def test_show(self):
        # Test if biobrick-list can show bbk
        resp = self.client.get(reverse('api:biobrick:biobrick-list'))
        self.assertGreater(len(resp.data['results']), 0)

    def test_order(self):
        # Test if biobrick-list can show the bbk in the specific order

        resp = self.client.get(reverse('api:biobrick:biobrick-list'))
        self.assertGreater(
            resp.data['results'][1]['part_name'],
            resp.data['results'][0]['part_name']
        )

        resp = self.client.get(reverse('api:biobrick:biobrick-list'),
                               {'order': '-uses'})
        self.assertGreater(
            resp.data['results'][0]['uses'],
            resp.data['results'][1]['uses']
        )

        resp = self.client.get(reverse('api:biobrick:biobrick-list'),
                               {'order': '2333?'})
        self.assertGreater(
            resp.data['results'][1]['part_name'],
            resp.data['results'][0]['part_name']
        )
