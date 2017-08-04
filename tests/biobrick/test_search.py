from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase


class TestSearch(APITestCase):
    # To test the search function. As the search function is highly
    # dependent on the indexes, you can only test it with given indexes.
    # And don't worry if it does not show the specific answer 'cause
    # the indexes may be different.

    def test_part_name(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'part_name': '034'})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        self.assertTrue('034' in resp.data['results'][0]['part_name'])

    def test_sequence(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'sequence': 'atac'})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        self.assertTrue('atac' in resp.data['results'][0]['sequence'])

    def test_suggestion(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'promotre'})
        self.assertEqual(len(resp.data['results']), 0)
        self.assertDictContainsSubset({'suggestion': 'promoter'}, resp.data)

    def test_q(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'promoter'})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        bbk_data = resp.data['results'][0]
        print('\nshort_desc: %s\ndescription: %s\nkey word: %s\n' % (bbk_data['short_desc'], bbk_data['description'], 'promoter'))

    def test_highlight(self):
        resp = self.client.get(reverse('api:biobrick:biobrick-search'),
                               {'q': 'promoter', 'highlight': None})
        self.assertGreaterEqual(len(resp.data['results']), 1)
        bbk_data = resp.data['results'][0]
        print('\nhighlighted: %s\nkey word: %s\n' % (bbk_data['highlighted'], 'promoter'))
