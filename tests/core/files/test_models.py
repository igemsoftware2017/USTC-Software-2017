from rest_framework.test import APITestCase

from biohub.core.files.models import File

from ._utils import open_sample


class Test(APITestCase):

    def test_create_from_file(self):
        sample1 = open_sample('1.txt')
        content = sample1.read()

        instance = File.objects.create_from_file(sample1)

        self.assertEqual(instance.mime_type, 'text/plain')
        self.assertEqual(instance.file.read(), content)

        sample1.close()
