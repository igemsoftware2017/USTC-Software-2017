import io
import subprocess
import logging

from django.core.files.storage import default_storage

from biohub.core.tasks import Task
from biohub.abacus.conf import settings
from biohub.abacus.result import AbacusAsyncResult

logger = logging.getLogger('biohub.abacus.tasks')


class AbacusTask(Task):

    async_result_class = AbacusAsyncResult

    def before_interrupt(self):

        if self.abacus_process is not None:
            self.abacus_process.terminate()
            self.abacus_process.wait()

    def run(self, input_file_name):

        self.abacus_process = None

        with io.StringIO('') as empty_file:
            output_file_name = default_storage.save(
                'abacus_output_' + input_file_name,
                empty_file
            )

        try:
            arguments = ['java',
                         '-jar', settings.ABACUS_JAR_PATH,
                         '-design',
                         '-dir', settings.ABACUS_DATABASE_PATH,
                         '-in', default_storage.path(input_file_name),
                         '-out', default_storage.path(output_file_name)
                         ]
            p = self.abacus_process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while 1:
                self.check_interrupt()
                try:
                    output, error = p.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    continue
                else:
                    break

            if p.returncode != 0 or b'ENERGY' not in output:
                default_storage.delete(output_file_name)
                error_msg = (
                    'ABACUS failed.\nExit Code: {code}\nStdout: {output}\nStderr: {error}'
                    .format(code=p.returncode, output=output.decode(), error=error.decode())
                )
                logger.error('Task {} failed.\n{}'.format(self.task_id, error_msg))
                raise RuntimeError(error_msg)
            else:
                # Success
                pass
        finally:
            default_storage.delete(input_file_name)

        return default_storage.url(output_file_name)
