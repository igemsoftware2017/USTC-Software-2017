import sys
import tempfile
import crontab
from os import path

from django.core.management import BaseCommand
from biohub.utils.path import modpath


class Command(BaseCommand):

    def add_arguments(self, parser):

        default_log_file = path.join(tempfile.gettempdir(), 'biohub.cronjob.log')

        parser.add_argument(
            '--log-file', '-l',
            dest='log_file',
            default=default_log_file,
            help='Log file for the job, default to {}'.format(default_log_file)
        )
        parser.add_argument(
            '--drop', '-d',
            dest='drop',
            action='store_true',
            default=False,
            help='Drop jobs without creating new ones'
        )

    def get_command(self):

        python_bin = sys.executable
        manage_py = path.abspath(path.join(modpath('biohub'), 'manage.py'))
        redirection = ' '.join(['>>' + self.log_file, '2>&1'])

        commands = [' '.join(('date', redirection))]
        for subcommand in ('refreshweight', 'update_index'):
            commands.append(
                ' '.join((python_bin, manage_py, subcommand, redirection))
            )

        return ' && '.join(commands)

    def get_job(self):

        self.stdout.write('Reading crontab...')
        cron = self.cron = crontab.CronTab(user=True)

        self.stdout.write('Dropping old jobs...')
        for job in cron.find_command('refreshweight'):
            job.delete()

        if self.drop:
            return None

        job = cron.new(self.get_command())
        job.setall("*/30 * * * *")

        return job

    def handle(self, log_file, drop, **kwargs):

        self.log_file = log_file
        self.drop = drop

        try:
            f = open(log_file, 'w')
            f.close()
        except OSError as exc:
            self.stderr.write(
                "Can't access location {}: {}".format(log_file, exc),
                self.style.ERROR
            )
            sys.exit(1)

        job = self.get_job()

        if drop:
            self.cron.write()
            self.stdout.write(
                'Old job dropped successfully.',
                self.style.SUCCESS
            )
        else:
            self.stdout.write('Installing new job: {!r}...'.format(job.command))
            self.cron.write()
            self.stdout.write(
                'New job installed successfully.',
                self.style.SUCCESS
            )
