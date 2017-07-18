import sys
from unittest import skipIf

from django.test import modify_settings, TestCase
from django.urls import reverse


@skipIf(all('core' not in s for s in sys.argv), 'For unknown reason this test '
        'case cannot cooperate with other tests.')
@modify_settings(INSTALLED_APPS={
    'append': 'tests.core'})
class Test(TestCase):

    def test_route(self):
        self.assertEqual(
            reverse('default:test:a'),
            '/test/a/')

        self.assertEqual(
            reverse('api:test:a'),
            '/api/test/a/')
