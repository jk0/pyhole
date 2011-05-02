import unittest

import pyhole.utils

class TestUtils(unittest.TestCase):
    def test_decode_entities(self):
        test_str = "<derp>herp a derp</derp>"
        self.assertEqual(pyhole.utils.decode_entities(test_str),
                'herp a derp')

    def test_decode_entities_2(self):
        test_str = "pewp&nbsp;shute"
        self.assertEqual(pyhole.utils.decode_entities(test_str),
                'pewp shute')

    def test_decode_entities_3(self):
        test_str = "&amp;"
        self.assertEqual(pyhole.utils.decode_entities(test_str), '&')

    def test_decode_entities_4(self):
        test_str = "&quot;"
        self.assertEqual(pyhole.utils.decode_entities(test_str), '"')

    def test_decode_entities_5(self):
        test_str = "&#8212;"
        self.assertEqual(pyhole.utils.decode_entities(test_str), '-')

    def test_decode_entities_6(self):
        test_str = "&#8217;"
        self.assertEqual(pyhole.utils.decode_entities(test_str), "'")

    def test_decode_entities_7(self):
        test_str = "&#8220;"
        self.assertEqual(pyhole.utils.decode_entities(test_str), "\"")

    def test_decode_entities_8(self):
        test_str = "&#8221;"
        self.assertEqual(pyhole.utils.decode_entities(test_str), "\"")

    def test_decode_entities_8(self):
        test_str = "&#8230;"
        self.assertEqual(pyhole.utils.decode_entities(test_str), "...")

    def test_decode_entities_9(self):
        test_str = "<[lol^>"
        self.assertEqual(pyhole.utils.decode_entities(test_str), "")

    def test_decode_entities_10(self):
        test_str = "<]*?>"
        self.assertEqual(pyhole.utils.decode_entities(test_str), "")

    def test_ensure_int(self):
        self.assertEqual(pyhole.utils.ensure_int("3"), 3)

    def test_ensure_int_2(self):
        self.assertEqual(pyhole.utils.ensure_int("\W"), None)

    def test_ensure_int_3(self):
        self.assertEqual(pyhole.utils.ensure_int("a"), None)
