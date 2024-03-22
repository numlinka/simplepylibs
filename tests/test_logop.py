# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# unit test

# std
import unittest

# tests
from logop import *


class TestLogop (unittest.TestCase):
    def test_logop(self):
        logs = Logging(stdout=False)
        logs.add_op(LogopStandardPlus())
        logs.info("test")
