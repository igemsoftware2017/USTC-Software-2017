try:
    import django_redis  # noqa
except ModuleNotFoundError:
    import warnings
    import sys

    warnings.warn(
        'Module `django_redis` is not available, '
        '**Tasks utility is disabled.**',
        RuntimeWarning)

    class Mock(object):

        def __getattr__(self, name):

            if name == '__file__':
                raise AttributeError

            return Mock()

        def __call__(self, *args, **kwargs):
            return Mock()

    sys.modules['django_redis'] = Mock()
