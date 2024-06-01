# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# unit test

# std
import os
import unittest

# tests
from dirstruct import *


class TestDirectory (unittest.TestCase):
    def test_directory(self):
        class TestDirectoryOld (Directory):
            folder_tests = "folder_tests"

        cwd = TestDirectoryOld()

        self.assertTrue(os.path.isdir(cwd.folder_tests))
        os.rmdir(cwd.folder_tests)


    def test_directory_plus(self):
        file_name = "file_name"
        current_working_directory = os.getcwd()

        class TestDirectoryPlus (Directory):
            file = FilePath(file_name)

        cwd = TestDirectoryPlus(current_working_directory)
        abscwd = TestDirectoryPlus(current_working_directory)
        cwd._include_ = False

        self.assertEqual(cwd, abscwd)
        self.assertEqual(cwd.file, file_name)
        self.assertEqual(abscwd.file, os.path.join(current_working_directory, file_name))
