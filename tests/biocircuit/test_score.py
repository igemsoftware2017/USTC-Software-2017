from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class TestScore(APITestCase):

    def test_no_nodes(self):
        resp = self.client.post(reverse('api:biocircuit:biocircuit-score'))
        self.assertDictContainsSubset({
            'status': 'failed',
            'detail': "'nodes'"
        }, resp.data)

    def test_different_typeof_nodes(self):
        resp = self.client.post(reverse('api:biocircuit:biocircuit-score'),
                                data={'nodes': 12}, format='json')
        self.assertDictContainsSubset({
            'status': 'failed',
            'detail': "'int' object is not iterable"
        }, resp.data)

    def test_valid_nodes(self):
        resp = self.client.post(reverse('api:biocircuit:biocircuit-score'),
                                data={'nodes': ['INPUT', 'OR0', 'NOT6']},
                                format='json')
        self.assertDictContainsSubset({
            'status': 'SUCCESS',
            'score': 16.5
        }, resp.data)
