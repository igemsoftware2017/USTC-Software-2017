import shutil
import filecmp
from os import path

from ._base import PluginTestCase
from django.core.management import call_command

CWD = path.dirname(__file__)
TEST_PATH = path.join(CWD, 'test')
EXPECT_PATH = path.join(CWD, 'expected')


def force_remove(path_name):
    try:
        shutil.rmtree(path_name)
    except FileNotFoundError:
        pass


class Test(PluginTestCase):

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

    def test_newplugin(self):
        call_command('newplugin', 'tests.core.plugins.test',
                     directory=CWD, verbosity=0)
        self.assertDirsIdentical(TEST_PATH, EXPECT_PATH)

    def test_installplugin(self):
        call_command('installplugin', 'tests.core.plugins.my_plugin')

        self.assertIn('tests.core.plugins.my_plugin',
                      self.current_settings['PLUGINS'])

    def test_removeplugin(self):
        self.test_installplugin()

        call_command('removeplugin', 'tests.core.plugins.my_plugin')

        self.assertNotIn('tests.core.plugins.my_plugin',
                         self.current_settings['PLUGINS'])

    def tearDown(self):
        force_remove(TEST_PATH)
