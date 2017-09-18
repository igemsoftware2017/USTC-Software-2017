import time
import decimal
import os.path as path

from django.db import connection
from django.utils.functional import cached_property
from django.core.management import BaseCommand

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
        ('doc_size_w', (1, '', False)),
        ('uses_w', (5, '', False)),
        ('review_total_w', (1, '', False)),
        ('review_count_w', (1, '', False)),
        ('rates', (2, 'max_rates', True)),
        ('rate_score', (3, 'max_rate_score', True)),
        ('stars', (2, 'max_stars', True)),
        ('watches', (2, 'max_watches', True))
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--chunk',
            '-c',
            type=int, default=1000
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

            while True:
                result = cursor.fetchmany(chunk)
                if not result:
                    break
                yield result

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
        """

        with connection.cursor() as cursor:
            sql = []

            for brick in bricks:

                full_scores = weight = 0

                for index, (field, (score, max_field, pass_if_zero)) in enumerate(self.parameters):

                    value = brick[index]
                    if value is None or not score or not value and pass_if_zero:
                        continue
                    value = decimal.Decimal(value)

                    if max_field and stats[max_field]:
                        value /= stats[max_field]

                    weight += score * value
                    full_scores += score

                if full_scores:
                    weight /= full_scores

                sql.append(
                    "SELECT '{}' as part_name, {} as weight".format(
                        brick[0],
                        weight
                    )
                )

            cursor.execute(
                "REPLACE INTO biobrick_biobrickweight (part_name, weight) {};".format(
                    ' UNION ALL '.join(sql)
                )
            )

        connection.commit()

    def handle(self, chunk, **kwargs):

        begin_time = time.time()
        stats = self.get_stats()

        self.stdout.write("Calculating...")
        counter = 0

        for bricks in self.iter_bricks(chunk):
            counter += len(bricks)
            self.calculate_bricks_weight(bricks, stats)

        self.stdout.write(
            "Done.\n{} bricks processed.\n{:.4f}s elapsed.".format(
                counter,
                time.time() - begin_time
            ),
            self.style.SUCCESS
        )
