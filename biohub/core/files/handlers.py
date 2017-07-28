from biohub.core.files import utils, models


def handle_permanent_file(request, field_name='file'):
    """
    Handles and stores the uploaded file to both file system and database,
    returns a File model instance.
    """
    return models.File.objects.create_from_file(request.FILES[field_name])


def handle_temporary_file(request, field_name='file'):
    """
    Handles and stores the uploaded file to temporary directory.

    NOTE THAT the file will be erased once closed.
    """
    return utils.store_temp_file(request.FILES[field_name])
