import os
import sys
import os.path
import argparse

import pytest
from django.core.management import BaseCommand

from biohub.utils.path import modpath

TESTS_PATH = os.path.join(modpath('biohub'), '..', 'tests')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'files',
            nargs=argparse.REMAINDER,
            help='You may specify the test files/directories to be executed.'
        )
        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help='Recreate test database (will slow down the test process), '
            'used when the database schema changed.'
        )

    def handle(self, files, recreate, *args, **options):
        if files:
            tests = filter(
                os.path.exists,
                map(lambda f: os.path.join(TESTS_PATH, f), files)
            )
        else:
            tests = [TESTS_PATH]

        pytest_args = [*tests, '-s', '--reuse-db', '--nomigrations']

        if recreate:
            pytest_args.extend(['--create-db'])

        sys.exit(pytest.main(pytest_args))
