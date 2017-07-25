from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class Test(APITestCase):

    def test_empty(self):
        # Test the empty list with no data in the database
        resp = self.client.get(reverse('api:biobrick:biobrick-list'))
        self.assertDictContainsSubset({'results': []}, resp.data)
