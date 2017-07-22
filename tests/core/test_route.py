from django.test import modify_settings, TestCase
from django.urls import reverse


@modify_settings(INSTALLED_APPS={
    'append': 'tests.core'})
class Test(TestCase):

    def test_route(self):
        from django.urls.resolvers import get_resolver
        get_resolver.cache_clear()
        self.assertEqual(
            reverse('default:test:a'),
            '/test/a/')

        self.assertEqual(
            reverse('api:test:a'),
            '/api/test/a/')
