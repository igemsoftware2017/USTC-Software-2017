class RemovalError(Exception):
    pass


class InstallationError(Exception):

    def __init__(self, original_exception):
        self.original_exception = original_exception

    def __str__(self):
        return str(self.original_exception)


class DatabaseError(InstallationError):

    pass


class URLConfError(InstallationError):

    pass
