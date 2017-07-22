import contextlib

from django.db import connection
from django.conf import settings


def _set_database_name(testing, alias, db_name):

    if not testing:
        return

    connection.close()
    settings.DATABASES[alias]['NAME'] = db_name
    connection.settings_dict['NAME'] = db_name


@contextlib.contextmanager
def patch_test_db(testing):
    """
    Reference: django/db/backends/base/creation.py:57

    A context manager to modify current database connection to simulate a test
    environment, just as what `manage.py test` does.

    The helper will be useful when migrating models for test database.
    """
    old_db_name = connection.settings_dict['NAME']
    test_db_name = connection.creation._get_test_db_name()
    alias = connection.alias

    _set_database_name(testing, alias, test_db_name)

    yield

    _set_database_name(testing, alias, old_db_name)
