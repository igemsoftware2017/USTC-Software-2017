import psutil
import subprocess
from urllib.request import urlopen
import urllib.parse as parse
import urllib.error

from django.conf import settings
from django.core.files.storage import default_storage

from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask

from .celery import app

logger = get_task_logger(__name__)


def add_params(url, **params):
    """
    Append or replace query params in `url` using `params`.
    """
    url = parse.unquote(url)
    parsed = parse.urlparse(url)
    existing = dict(parse.parse_qsl(parsed.query))
    existing.update(params)
    return parse.urlunparse(
        parse.ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=parsed.path,
            params=parsed.params,
            query=parse.urlencode(existing),
            fragment=parsed.fragment
        )
    )


@app.task(bind=True, base=AbortableTask)
def run_abacus(self, input_file, callback, output_file, output_file_url):

    # Install signal handler for SIGINT (a bit hacky, but it works)
    # See: https://stackoverflow.com/questions/45650904/in-celery-how-to-abort-running-tasks-when-workers-are-about-to-shut-down
    import celery.platforms

    p = None

    def int_handler(signum, frame):

        if p is not None:
            p.kill()
            p.wait()

    celery.platforms.signals['INT'] = int_handler

    # Task begins
    task_id = self.request.id
    logger.info('Task %s started.' % task_id)
    success = True

    # Execute ABACUS
    try:
        arguments = settings.ABACUS_BASE_ARGUMENTS + [
            '-in', default_storage.path(input_file),
            '-out', default_storage.path(output_file),
        ]

        p = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        psutil.Process(p.pid).nice(10)

        output, err = p.communicate()

        if p.returncode != 0 or b'ENERGY' not in output:
            # ABACUS failed.
            error_msg = (
                'Task %s failed.\ncode: %s.\nout: %s.\nerr: %s.'
                % (
                    task_id,
                    p.returncode,
                    output.decode(),
                    err.decode()
                )
            )
            logger.error(error_msg)
            callback = add_params(callback, task_id=task_id, error=True)
            default_storage.delete(output_file)
            success = False
        else:
            callback = add_params(callback, task_id=task_id, output=output_file_url)
    finally:
        default_storage.delete(input_file)

    # Invoke callback
    try:
        urlopen(callback, timeout=5)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        logger.error('Fail to fetch %s.\nReason: %s' % (callback, e))
    finally:
        logger.info('Task %s finished.' % task_id)

        if success:
            return output_file_url
        else:
            raise Exception(error_msg)
