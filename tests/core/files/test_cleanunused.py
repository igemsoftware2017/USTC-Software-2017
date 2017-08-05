from rest_framework.test import APITestCase
from unittest import skipIf
from django.test import modify_settings, override_settings
from django.conf import settings

from biohub.core.files.clean_unused import clean_unused
from biohub.accounts.models import User
from ._utils import open_sample


@skipIf(
    'tests.core.files.cleanunused_tests' not in settings.INSTALLED_APPS,
    '')
@modify_settings(INSTALLED_APPS={
    'append': 'tests.core.files.cleanunused_tests'
})
@override_settings(DEBUG=True)
class Test(APITestCase):

    def test_cleanunused(self):
        from tests.core.files.cleanunused_tests.models import TestModel

        me = User.objects.create_test_user('me')
        self.client.force_authenticate(me)
        sample = open_sample('1.txt')

        erased = []
        exists = []

        for i in range(10):
            sample.seek(0)
            url = self.client.post('/files/upload/', {'file': sample})\
                .data['file']

            if i & 1:
                TestModel.objects.create(text='asgasg[{}]()afsadg'.format(url))
                exists.append(url)
            else:
                erased.append(url)

        clean_unused()

        for url in erased:
            self.assertEqual(404, self.client.get(url).status_code)

        for url in exists:
            self.assertEqual(200, self.client.get(url).status_code)
