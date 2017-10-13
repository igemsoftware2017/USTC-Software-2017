from rest_framework.test import APITestCase
from django.urls import reverse
from django.test import override_settings

from biohub.accounts.models import User

from ._utils import open_sample


@override_settings(DEBUG=True)
class Test(APITestCase):

    def test_upload_fail(self):
        url = reverse('default:files:upload')
        self.assertEqual(403,
                         self.client.post(url, {}).status_code)

    def test_upload(self, filename='2.txt.txt'):
        url = reverse('default:files:upload')
        me = User.objects.create_test_user('me')
        self.client.force_authenticate(me)

        sample = open_sample(filename)
        content = sample.read()
        sample.seek(0)

        # Phase 1
        resp = self.client.post(url + '?store_db=1', dict(file=sample))
        self.assertIn('id', resp.data)
        self.assertEqual(resp.data['name'], filename)
        self.assertEqual(
            content,
            b''.join(
                self.client.get(resp.data['file']).streaming_content))

        # Phase 2
        sample.seek(0)
        resp = self.client.post(url, dict(file=sample))
        self.assertNotIn('id', resp.data)
        self.assertEqual(
            content,
            b''.join(
                self.client.get(resp.data['file']).streaming_content))

    def test_upload2(self):
        self.test_upload('2')
