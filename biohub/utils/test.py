def skip_if_no_environ(name):
    import os
    import unittest

    return unittest.skipIf(not os.environ.get(name, 0), '')
