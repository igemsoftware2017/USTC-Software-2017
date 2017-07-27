from rest_framework.test import APITestCase
from django.test import modify_settings

from biohub.core.files.clean_unused import clean_unused
from biohub.accounts.models import User
from ._utils import open_sample


@modify_settings(INSTALLED_APPS={
    'append': 'tests.core.files.cleanunused_tests'
})
class Test(APITestCase):

    def test_cleanunused(self):
        from tests.core.files.cleanunused_tests.models import TestModel

        me = User.objects.create_user(username='me', password='me')
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
