import os
import errno
import os.path

from django.core.management.commands.startapp import Command as StartappCommand
from django.core.management import CommandError


from django.conf import settings


class Command(StartappCommand):

    def handle(self, **options):
        app_name, target = options.pop('name'), options.pop('directory')

        # Set the top directory to root of Biohub instead of current
        # path.
        if target is None:
            target = os.path.join(settings.BIOHUB_DIR, app_name)

            try:
                os.makedirs(target)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    message = "'%s' already exists" % target
                else:
                    message = e
                raise CommandError(message)

        # Use custom app template
        if options['template'] is None:
            options['template'] = os.path.join(
                settings.BIOHUB_CORE_DIR, 'app_template')

        super(StartappCommand, self).handle('app', app_name, target, **options)
