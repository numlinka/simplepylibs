# Licensed under the LGPL 3.0 License.
# simplepylibs by numlinka.
# unit test

# std
import unittest

# tests
from ezconfiguration import *


class TestConfiguration (unittest.TestCase):
    def test_basic(self):
        con = Configuration()
        con._new("value_int", int, 100, range(0, 1000))
        con._new("value_float", float, 10.0)
        con._new("value_str", str, "Hello world.")

        self.assertEqual(con.value_int, 100)
        self.assertEqual(con.value_float, 10.0)
        self.assertEqual(con.value_str, "Hello world.")
        self.assertIsInstance(con.value_int, int)
        self.assertIsInstance(con.value_float, float)
        self.assertIsInstance(con.value_str, str)

        con.value_int.set(200)

        self.assertEqual(con.value_int, 200)


    def test_range(self):
        con = Configuration()
        con._new("value_int", int, 100, range(0, 1000))

        self.assertEqual(con.value_int.values(), tuple(range(0, 1000)))

        with self.assertRaises(ValueOutOfRange):
            con.value_int.set(-1)


    def test_raise(self):
        con = Configuration()
        con._new("value_int", int, 100, range(0, 1000))

        with self.assertRaises(keyAlreadyExist):
            con._new("value_int", int, 100, range(0, 1000))

        with self.assertRaises(KeyDoesNotExist):
            con.value_int2


    def test_load_data(self):
        data = {
            "value_int": 200,
            "value_float": 20.0,
            "value_str": "Hello world!"
        }

        con = Configuration()
        con._new("value_int", int, 100, range(0, 1000))
        con._new("value_float", float, 10.0)
        con._new("value_str", str, "Hello world.")

        con._load_dict(data)

        self.assertEqual(con.value_int, 200)
        self.assertEqual(con.value_float, 20.0)
        self.assertEqual(con.value_str, "Hello world!")


    def test_invalid(self):
        data = {
            "value_int": 200,
            "value_int2": 300
        }

        con = Configuration()
        con._new("value_int", int, 100, range(0, 1000))

        self.assertEqual(con._load_dict(data), ["value_int2"])

        con._new_invalid("value_int3", 400)
        con._new("value_int2", int, 100, range(0, 1000))
        con._new("value_int3", int, 100, range(0, 1000))

        self.assertEqual(con.value_int, 200)
        self.assertEqual(con.value_int2, 300)
        self.assertEqual(con.value_int3, 400)


    def test_save(self):
        data = {
            "value_int": 200,
            "value_float": 20.0,
            "value_str": "Hello world!"
        }

        con = Configuration()
        con._new("value_int", int, 100, range(0, 1000))
        con._new("value_float", float, 10.0)
        con._new("value_str", str, "Hello world.")
        con._load_dict(data)

        self.assertEqual(con._save_dict(), data)


    def test_save_invalid(self):
        data = {
            "value_int": 200,
            "value_float": 20.0,
            "value_str": "Hello world!"
        }

        con = Configuration()
        con._load_dict(data)

        self.assertEqual(con._save_dict(), data)
