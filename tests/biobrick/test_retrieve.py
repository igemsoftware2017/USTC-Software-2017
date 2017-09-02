from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class TestRetrieve(APITestCase):
    # To test the list rest-api

    def test_retrieve(self):
        bbk7284 = {
            'part_name': 'BBa_J52025',
            'uses': 0,
            "short_desc": "rLUC"
        }
        resp = self.client.get(
            reverse('api:biobrick:biobrick-detail', args=(7284,))
        )
        self.assertEqual(resp.status_code, 200)
        self.assertDictContainsSubset(bbk7284, resp.data)

    def test_no_result(self):
        resp = self.client.get(
            reverse('api:biobrick:biobrick-detail', args=(100,)))
        self.assertEqual(resp.status_code, 404)
        self.assertDictContainsSubset({'detail': 'Not found.'}, resp.data)
