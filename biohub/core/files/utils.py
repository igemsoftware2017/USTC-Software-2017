import tempfile
import os.path
import functools
import mimetypes

from django.core.files.storage import default_storage
from django.core.files import File as FileWrapper


def stash_file_pos(func):
    """
    A decorator to ensure the file-like object passed in will be reset to its
    original position when the function returns.
    """

    @functools.wraps(func)
    def inner(fd):

        current_pos = fd.tell()
        result = func(fd)
        fd.seek(current_pos)

        return result

    return inner


@stash_file_pos
def store_file(fd):
    """
    Given a file-like object and stores it with default storage system.

    Returns a tuple (file_name, mime_type), where the file name is relative to
    MEDIA_ROOT.
    """

    name = default_storage.save(os.path.basename(fd.name), fd)

    return name, mimetypes.guess_type(name)[0] or ''


@stash_file_pos
def store_temp_file(fd):
    """
    Given a file-like object and dumps it to the temporary directory.

    Returns the temporary file object.
    """
    temp_file = tempfile.NamedTemporaryFile(
        encoding=getattr(fd, 'encoding', None))

    source = FileWrapper(fd)
    for chunk in source.chunks():
        temp_file.write(chunk)

    temp_file.seek(0)

    return temp_file
