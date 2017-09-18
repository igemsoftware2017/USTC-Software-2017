from rest_framework import status, exceptions


class SpiderError(Exception):

    def __init__(self, *args, **kwargs):
        self.details = self.message(*args, **kwargs)

    def message(self, *args, **kwargs):
        return self.error_message_template.format(*args, **kwargs)

    @property
    def api_exception(self):
        return self.exception_class(self.details)


class ResourceNotFoundError(SpiderError):

    error_message_template = 'Resource {} cannot be found on igem offical pages.'
    status_code = status.HTTP_404_NOT_FOUND
    exception_class = exceptions.NotFound


class NetworkError(SpiderError):

    error_message_template = 'Resource {} cannot be fetched due to network problem: {}.'
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    exception_class = exceptions.APIException
