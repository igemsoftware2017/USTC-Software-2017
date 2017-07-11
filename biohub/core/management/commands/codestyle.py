import os
import os.path as path
import sys

from django.core.management import BaseCommand
from django.conf import settings

PATH_TO_CHECK = path.join(settings.BIOHUB_DIR, '..')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        cmd = os.system(' '.join(['flake8', PATH_TO_CHECK]))

        if os.WEXITSTATUS(cmd):
            sys.exit(1)
