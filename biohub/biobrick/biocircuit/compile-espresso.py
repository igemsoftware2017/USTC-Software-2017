import sys
import os
import platform

sysstr = sys.platform
a, b, *c = platform.python_version().split('.')
if sysstr == "linux" or sysstr == "linux2" or sysstr == "darwin":
    os.system(
        "gcc -w ./espresso/*.c -fPIC -shared -o espresso.so -lpython" + a + "." + b + "m -I/usr/include/python" + a + "." + b + "m/")
elif sysstr == "win32":
    os.system(
        "gcc -w ./espresso/*.c -mdll -D MS_WIN32 -o espresso.pyd -lpython" + a + b + " -IC:\Python" + a + b + "\include -LC:\Python" + a + b + "\libs")
elif sysstr == "win64":
    os.system(
        "gcc -w ./espresso/*.c -mdll -D MS_WIN64 -o espresso.pyd -lpython" + a + b + " -IC:\Python" + a + b + "\include -LC:\Python" + a + b + "\libs")
else:
    print('Unsupported OS!')
