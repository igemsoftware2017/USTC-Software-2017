import os.path as path
import argparse
import subprocess

BASE_DIR = path.abspath(path.dirname(__file__))

celery_process = None
server_process = None


def main(arguments):

    global celery_process, server_process

    print('Starting celery...')
    celery_process = subprocess.Popen(
        ['celery', '-E', '-A', 'abacus_server', 'worker',
         '--concurrency', str(arguments.concurrency),
         '-l', 'info',
         '-n', 'abacus_server@localhost:%s' % arguments.port],
        cwd=BASE_DIR, stdout=subprocess.PIPE
    )

    try:
        output, _ = celery_process.communicate(timeout=.5)
    except subprocess.TimeoutExpired:
        # Celery starts successfully
        print('Celery process started successfully!')
    else:
        return

    print('Starting server...')
    server_process = subprocess.Popen(['./manage.py', 'runserver', str(arguments.port)], cwd=BASE_DIR)

    server_process.communicate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='abacus_server')
    parser.add_argument('--port', default=8888, type=int)
    parser.add_argument('--concurrency', default=4, type=int)

    try:
        main(parser.parse_args())
    except KeyboardInterrupt:
        print('Terminating...')
        if celery_process is not None:
            celery_process.wait()
            celery_process = None
        print('Celery process terminated!')
        if server_process is not None:
            server_process.wait()
            server_process = None
        print('Server process terminated!')
    finally:
        if celery_process is not None and celery_process.returncode is None:
            celery_process.terminate()
            celery_process.wait()
            print('Celery process terminated!')
        if server_process is not None and server_process.returncode is None:
            server_process.terminate()
            server_process.wait()
            print('Server process terminated!')
