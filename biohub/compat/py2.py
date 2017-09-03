# Monkey patch of several python2 functions.

for key, value in (
    ("xrange", range),
    ("unichr", chr)
):
    __builtins__[key] = value
