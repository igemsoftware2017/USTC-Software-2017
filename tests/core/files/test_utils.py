import os.path as path

from django.core.files.storage import default_storage
from rest_framework.test import APITestCase

from biohub.core.files import utils

from ._utils import open_sample


class Test(APITestCase):

    def test_store_file(self):

        sample1 = open_sample('1.txt')
        content = sample1.read()

        name, _ = utils.store_file(sample1)
        self.assertEqual(content, default_storage.open(name).read())

        sample1.close()

    def test_store_temp_file(self):

        sample2 = open_sample('2.txt')
        content = sample2.read()

        tmpfile = utils.store_temp_file(sample2)
        self.assertEqual(content, tmpfile.read())

        sample2.close()

        name = tmpfile.name
        tmpfile.close()
        self.assertFalse(path.exists(name))

    def test_url_to_filename(self):

        from django.conf import settings

        name = 'a/b/c'
        url = settings.MEDIA_URL + name
        self.assertEqual(utils.url_to_filename(url), name)
