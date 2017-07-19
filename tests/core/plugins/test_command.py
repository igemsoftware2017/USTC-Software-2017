import shutil
import filecmp
from os import path

from django.test import TestCase
from django.core.management import call_command

CWD = path.dirname(__file__)
TEST_PATH = path.join(CWD, 'test')
EXPECT_PATH = path.join(CWD, 'expected')


def force_remove(path_name):
    try:
        shutil.rmtree(path_name)
    except FileNotFoundError:
        pass


class Test(TestCase):

    def setUp(self):
        force_remove(TEST_PATH)

    def assertDirsIdentical(self, dir1, dir2):
        result = filecmp.dircmp(dir1, dir2)

        if result.diff_files or result.left_only or result.right_only:
            raise AssertionError(
                "'%s' and '%s' is not exactly identical.\n"
                "Diff files: %r\n"
                "Left only:  %r\n"
                "Right only: %r\n" % (
                    dir1, dir2,
                    result.diff_files,
                    result.left_only,
                    result.right_only))

    def test_command(self):
        call_command('newplugin', 'test', 'tests.core.plugins.test',
                     directory=CWD)
        self.assertDirsIdentical(TEST_PATH, EXPECT_PATH)

    def tearDown(self):
        force_remove(TEST_PATH)
