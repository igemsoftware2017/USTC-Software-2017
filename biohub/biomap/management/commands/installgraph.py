import time
import json
import os.path as path

from django.db import connection
from django.utils.functional import cached_property
from django.core.management import BaseCommand

from biohub.utils.path import modpath
from biohub.biomap.builder import builder


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--chunk',
            '-c',
            type=int, default=1000,
            help='Items processed at once.'
        )

    @cached_property
    def fetch_sql(self):
        """
        Loads and returns SQL statements to fetch bricks data.
        """
        location = path.join(modpath('biohub.biomap.sql'), 'fetch_bricks.sql')

        with open(location, 'r') as f:
            return f.read()

    def iter_bricks(self, chunk):
        """
        Executes `fetch_sql` and yields `chunk` records at a time.
        """

        with connection.cursor() as cursor:

            cursor.execute(self.fetch_sql)
            cols = [col[0] for col in cursor.description]

            while True:
                result = cursor.fetchmany(chunk)
                if not result:
                    break
                yield (dict(zip(cols, row)) for row in result)

    def process(self, options):

        chunk = options['chunk']

        self.stdout.write("Calculating...")

        counter = 0

        for bricks in self.iter_bricks(chunk):

            counter += self.handle_bricks(bricks)

            self.stdout.write(
                'Processed {} brick(s)'.format(counter)
            )

    def handle_bricks(self, bricks):

        counter = 0
        for brick in bricks:
            builder.build(brick['part_name'], json.loads(brick['ruler'])['sub_parts'], force=True)
            counter += 1

        return counter

    def handle(self, **options):

        begin_time = time.time()

        self.process(options)

        self.stdout.write(
            '{:.4f}(s) elapsed.'.format(time.time() - begin_time)
        )
