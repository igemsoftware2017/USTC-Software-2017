from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class TestBiocircuit(APITestCase):

    def test_less_than_two_digits(self):
        # Test less than two digits
        resp = self.client.get(reverse('api:biocircuit:biocircuit-build', args=('0---',)))
        self.assertDictContainsSubset({
            'status': 'failed',
            'detail': 'At least two digits are required.'
        }, resp.data)

    def test_irregular_digits(self):
        resp = self.client.get(reverse('api:biocircuit:biocircuit-build', args=('10-0-1',)))
        self.assertDictContainsSubset({
            'status': 'failed',
            'detail': 'expected 2 inputs, got 3'
        }, resp.data)

    def test_biocircuit(self):
        resp = self.client.get(reverse('api:biocircuit:biocircuit-build', args=('11--',)))
        resp_nodes = [
            {*circuit['nodes'], circuit['score']}
            for circuit in resp.data
        ]
        expected_nodes = [
            {'INPUT', 'OR0', 'NOT3', 10},
            {'INPUT', 'OR0', 'NOT3', 10},
            {'INPUT', 'OR0', 'NOT6', 16.5},
            {'INPUT', 'OR0', 'NOT6', 16.5},
            {'INPUT', 'OR0', 'NOT5', 17.5}
        ]
        self.assertListEqual(resp_nodes, expected_nodes)
