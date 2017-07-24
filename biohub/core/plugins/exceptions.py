class PluginError(Exception):

    def __init__(self, original_exception):
        self.original_exception = original_exception

    def __str__(self):
        return str(self.original_exception)


class RemovalError(PluginError):
    pass


class InstallationError(PluginError):
    pass


class DatabaseError(RemovalError, InstallationError):

    pass


class URLConfError(RemovalError, InstallationError):

    pass
