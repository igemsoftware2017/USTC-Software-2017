import sys
import requests
import tempfile


def download(url, dest=None, suffix=None, stdout=sys.stdout):

    if dest is None:
        dest_fp, dest_name = tempfile.mkstemp(suffix=suffix)
        f = open(dest_fp, 'w+b')
    else:
        f = open(dest, 'w+b')
        dest_name = dest

    stdout.write('Downloading from {}...\n'.format(url))
    r = requests.get(url, stream=True)

    total = int(r.headers.get('Content-Length', 0))
    received = 0
    last_length = 0

    for chunk in r.iter_content(chunk_size=1024 * 1024):
        if chunk:
            f.write(chunk)
            received += len(chunk)

            if total:
                message = 'Completed {}%'.format(received / total * 100)
            else:
                message = 'Received {} bytes.'.format(received)

            stdout.write('\b' * last_length)
            stdout.flush()
            stdout.write(message)
            stdout.flush()
            last_length = len(message)
    else:
        stdout.write('\b' * last_length)
        stdout.flush()

    stdout.write('Downloaded %s.\n' % dest_name)

    f.seek(0)
    return f, dest_name
