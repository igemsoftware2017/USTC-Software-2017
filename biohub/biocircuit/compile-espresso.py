import sys
import os
import platform

sysstr = sys.platform
dirname = os.path.dirname(os.path.abspath(__file__))
a, b, *c = platform.python_version().split('.')


def make_path(*args):
    return os.path.join(dirname, *args)


if sysstr == "linux" or sysstr == "linux2" or sysstr == "darwin":
    commands = ['gcc', '-w', make_path('espresso', '*.c'),
                '-fPIC', '-shared',
                '-o', make_path('espresso.so'),
                '-lpython{a}.{b}m',
                '-I/usr/local/include/python{a}.{b}m/',
                '-I/usr/include/python{a}.{b}m/']
elif sysstr in ["win32", "win64"]:
    commands = ['gcc', '-w', make_path('espresso', '*.c'),
                '-mdll',
                '-D', 'MS_{}'.format(sysstr.upper()),
                '-o', make_path('espresso.pyd'),
                '-lpython{a}{b}',
                r'-IC:\Python{a}{b}\include',
                r'-LC:\Python{a}{b}\libs']
else:
    print('Unsupported OS!')
    sys.exit(1)

if __name__ == '__main__':
    sys.exit(
        os.system(' '.join(part.format(**globals()) for part in commands))
    )
