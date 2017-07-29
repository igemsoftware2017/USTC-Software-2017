import os.path

from rest_framework.test import APITestCase, APIRequestFactory

from biohub.core.files import handlers

from ._utils import open_sample


def create_sample_request(name):

    fd = open_sample(name)
    request = APIRequestFactory().post('', {'file': fd})
    fd.seek(0)

    return fd, request


class Test(APITestCase):

    def test_handle_permanent_file(self):
        sample, request = create_sample_request('1.txt')
        instance = handlers.handle_permanent_file(request)

        self.assertEqual(sample.read(), instance.file.read())

        sample.close()

    def test_handle_temporary_file(self):
        sample, request = create_sample_request('1.txt')
        tmpfile = handlers.handle_temporary_file(request)

        self.assertEqual(sample.read(), tmpfile.read())

        sample.close()
        name = tmpfile.name
        tmpfile.close()

        self.assertFalse(os.path.exists(name))
