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
        parser.add_argument(
            '--capture-stdout', '-cs',
            action='store_true',
            default=False,
            dest='capture_stdout',
            help='Tell pytest to capture stdout when certain tests fail.')

    def handle(self, files, recreate, capture_stdout, *args, **options):
        if files:
            real_paths = [os.path.join(TESTS_PATH, f) for f in files]
            missing = [f for f in real_paths if not os.path.exists(f)]

            if missing:
                self.stdout.write(
                    'The path(s) below can not be accessed:\n%s' % '\n'.join(missing),
                    self.style.WARNING
                )
                self.stdout.write('Tests aborted.', self.style.ERROR)
                sys.exit(1)

            tests = real_paths
        else:
            tests = [TESTS_PATH]

        pytest_args = [*tests, '--reuse-db', '--nomigrations']

        if recreate:
            pytest_args.extend(['--create-db'])

        os.environ['BIOHUB_TESTING'] = '1'

        if not capture_stdout:
            pytest_args.extend(['-s'])

        sys.exit(pytest.main(pytest_args))
