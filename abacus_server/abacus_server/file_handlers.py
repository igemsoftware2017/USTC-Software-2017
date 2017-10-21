from collections import namedtuple

from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.files.storage import default_storage

FakeFile = namedtuple('FakeFile', 'name')


class StraightHandler(TemporaryFileUploadHandler):
    """
    A file handler to directly store uploaded files.
    """

    def file_complete(self, file_size):
        super(StraightHandler, self).file_complete(file_size)

        self.file_name = default_storage.save(self.file_name + '_1', self.file)

        # Hacky approach to avoid annoying error.
        if hasattr(self.file.file, '_closer'):
            self.file.file._closer.close_called = True

        self.file = FakeFile(name=self.file_name)
        return self.file
