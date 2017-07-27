from django.db import models

from biohub.core.files.utils import store_file


class FileManager(models.Manager):

    def create_from_file(self, fd):
        """
        Creates and returns an instance with a file-like object `fd`.
        """
        name, mime_type = store_file(fd)

        return self.create(
            mime_type=mime_type,
            file=name)


class File(models.Model):

    file = models.FileField()
    mime_type = models.CharField(max_length=50)

    objects = FileManager()
