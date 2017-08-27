from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase

from biohub.biobrick.models import Biobrick

# from biohub.biobrick.models import Biobrick


class TestRetrieve(APITestCase):
    # To test the list rest-api

    def setUp(self):
        self.bbk = Biobrick.objects.create(
            part_name='asga',
            sequence='asdfahg',
            short_desc='sdgaga'
        )
        self.bbk_dict = {
            'part_name': 'asga',
            'sequence': 'asdfahg',
            'short_desc': 'sdgaga'
        }

    def test_retrieve(self):
        resp = self.client.get(
            reverse('api:biobrick:biobrick-detail', args=(self.bbk.pk,)))
        self.assertEqual(resp.status_code, 200)
        self.assertDictContainsSubset(self.bbk_dict, resp.data)

    def test_no_result(self):
        resp = self.client.get(
            reverse('api:biobrick:biobrick-detail', args=(self.bbk.pk + 1,)))
        self.assertEqual(resp.status_code, 404)
        self.assertDictContainsSubset({'detail': 'Not found.'}, resp.data)
