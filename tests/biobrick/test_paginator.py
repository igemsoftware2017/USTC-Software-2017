from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class TestPaginator(APITestCase):
    # To test the list paginator

    def test_default(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-list'))
        self.assertEqual(len(resp.data['results']), 20)

    def test_pagesize(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-list'),
                               {'pagesize': 13})
        self.assertEqual(len(resp.data['results']), 13)

    def test_maximum_size(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-list'),
                               {'pagesize': 400})
        self.assertEqual(len(resp.data['results']), 50)

    def test_less_than_zero_size(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-list'),
                               {'pagesize': -12})
        self.assertEqual(len(resp.data['results']), 20)

    def test_zero_size(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-list'),
                               {'pagesize': 0})
        self.assertEqual(len(resp.data['results']), 20)

    def test_not_integer_size(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-list'),
                               {'pagesize': 'hihihi'})
        self.assertEqual(len(resp.data['results']), 20)
