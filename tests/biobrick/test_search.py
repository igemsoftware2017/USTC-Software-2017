from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class TestSearch(APITestCase):
    # To test the search function. As the search function is highly
    # dependent on the indexes, you can only test it with given indexes.
    # And don't worry if it does not show the specific answer 'cause
    # the indexes may be different.

    def test_suggestion(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'promotre'})
        self.assertEqual(len(resp.data['results']), 0)
        self.assertDictContainsSubset({'suggestion': 'promoter'}, resp.data)

    def test_q_desc(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'RBS'})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        self.assertIn('RBS', resp.data['results'][0]['short_desc'])

    def test_highlight_desc(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'RBS', 'highlight': None})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        self.assertIn('<div class="highlight">RBS</div>',
                      resp.data['results'][0]['short_desc'])

    def test_q_name(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'BBa_J63006'})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['part_name'], 'BBa_J63006')

    def test_highlight_name(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'bba', 'highlight': None})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        self.assertIn('<div class="highlight">BBa</div>',
                      resp.data['results'][0]['part_name'])
