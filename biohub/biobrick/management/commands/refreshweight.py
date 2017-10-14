import sys
import time
import decimal
import math
from datetime import timedelta
import os.path as path

from django.db import connection
from django.utils.timezone import now
from django.utils.functional import cached_property
from django.core.management import BaseCommand, call_command

from biohub.utils.path import modpath


class Command(BaseCommand):

    # (field_name, (weight, max_field_name, pass_if_zero))
    # The order MUST be strictly the same as that in fetch.sql
    parameters = (
        ('part_name', (0, '', False)),
        ('favorite', (1, '', False)),
        ('has_barcode', (1, '', False)),
        ('status_w', (4, '', False)),
        ('sample_status_w', (4, '', False)),
        ('works_w', (1, '', False)),
        ('uses_w', (5, '', False)),
        ('review_total_w', (1, '', False)),
        ('review_count_w', (1, '', False)),
        ('rates', (2, 'max_rates', True)),
        ('rate_score', (3, 'max_rate_score', True)),
        ('stars', (2, 'max_stars', True)),
        ('watches', (2, 'max_watches', True))
    )

    tolerance = 1e-4

    def add_arguments(self, parser):
        parser.add_argument(
            '--action', '-A',
            choices=['calc', 'invalidate'],
            default='calc'
        )
        parser.add_argument(
            '--chunk',
            '-c',
            type=int, default=1000,
            help='Items processed at once.'
        )
        parser.add_argument(
            '--update-index', '-u',
            action='store_true', default=False,
            help='Indexes will be updated if specified.'
        )
        parser.add_argument(
            '--age', '-a',
            default='29m',
            help='Time back to consider objects new. Should in the form of /\d+[HhMmSs]/.'
        )

    @cached_property
    def fetch_sql(self):
        """
        Loads and returns SQL statements to fetch bricks data.
        """
        location = path.join(modpath('biohub.biobrick.sql'), 'weight', 'fetch.sql')

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

    def get_stats(self):
        """
        Fetches some statistical data.
        """
        from biohub.biobrick.models import BiobrickMeta
        from django.db.models import Max

        self.stdout.write(
            "Collecting statistical data..."
        )
        return dict(
            max_rate_score=5,
            **BiobrickMeta.objects.aggregate(
                max_rates=Max('rates'),
                max_stars=Max('stars'),
                max_watches=Max('watches')
            )
        )

    def calculate_bricks_weight(self, bricks, stats):
        """
        For a given bulk of bricks, calculates and updates weight value for each
        record, with the help of statistical data specified by `stats`.

        Returns the number of bricks processed.
        """

        current_time = connection.ops.adapt_datetimefield_value(now())

        with connection.cursor() as cursor:
            sql = []
            total_counter = updated_counter = 0

            for brick in bricks:

                total_counter += 1
                full_scores = weight = 0

                for field, (score, max_field, pass_if_zero) in self.parameters:

                    value = brick[field]
                    if value is None or not score or not value and pass_if_zero:
                        continue
                    value = decimal.Decimal(value)

                    if max_field and stats[max_field]:
                        value /= stats[max_field]

                    weight += score * value
                    full_scores += score

                if full_scores:
                    weight /= full_scores

                old_weight = brick['old_weight']

                if old_weight is None or not math.isclose(old_weight, weight, rel_tol=self.tolerance):

                    sql.append(
                        "SELECT '{}', {}, '{}'".format(
                            brick['part_name'],
                            weight,
                            current_time
                        )
                    )
                    updated_counter += 1

            if updated_counter:
                cursor.execute(
                    "REPLACE INTO biobrick_biobrickweight (part_name, weight, weight_updated_time) {};".format(
                        ' UNION ALL '.join(sql)
                    )
                )

        connection.commit()
        return total_counter, updated_counter

    def calc(self, options):

        stats = self.get_stats()
        chunk = options['chunk']

        self.stdout.write("Calculating...")
        total_counter = updated_counter = 0

        for bricks in self.iter_bricks(chunk):
            processed, updated = self.calculate_bricks_weight(bricks, stats)
            total_counter += processed
            updated_counter += updated

        self.stdout.write(
            "Done.\n{} bricks processed,{} bricks updated.".format(
                total_counter, updated_counter
            ),
            self.style.SUCCESS
        )

    def invalidate(self):

        from biohub.biobrick.models import BiobrickWeight

        self.stdout.write('Invalidating weights...')
        BiobrickWeight.objects.update(weight_updated_time=now())
        self.stdout.write('Done.', self.style.SUCCESS)

    def parse_age(self, age):

        if not age:
            raise ValueError('Age cannot be empty.')

        suffix = age[-1].lower()
        if suffix not in 'hms':
            raise ValueError('Age should end with s/m/h.')

        num = age[:-1]
        try:
            num = int(age[:-1])
        except ValueError:
            raise ValueError('"{}" is not a valid integer.'.format(num))

        return timedelta(**dict({
            {'h': 'hours', 'm': 'minutes', 's': 'seconds'}[suffix]: num
        }))

    def parse_update_index(self, options):

        to_update_index = options['update_index']
        age = options['age']

        if not to_update_index:
            return to_update_index, None

        try:
            return to_update_index, self.parse_age(age)
        except ValueError as exc:
            self.stdout.write(str(exc), self.style.ERROR)
            sys.exit(1)

    def handle(self, action, **options):

        to_update_index, age = self.parse_update_index(options)

        begin_time = time.time()

        if action == 'calc':
            self.calc(options)
        elif action == 'invalidate':
            self.invalidate()

        if to_update_index:
            from multiprocessing import cpu_count

            start = (now() - age).strftime('%Y-%m-%dT%H:%M:%S%z')

            self.stdout.write('Indexing weights from {}'.format(start))
            call_command('update_index', start_date=start, workers=cpu_count())

        self.stdout.write(
            '{:.4f}(s) elapsed.'.format(time.time() - begin_time)
        )
