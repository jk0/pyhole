#   Copyright 2011 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""Pyhole Utils Unit Tests"""

import os
import sys
import unittest

from pyhole import utils


class TestUtils(unittest.TestCase):
    def setUp(self):
        utils.write_file("tests", "pyhole_test_file", "foo")
        self.new_file = utils.get_home_directory() + "tests/pyhole_test_file"

    def tearDown(self):
        os.unlink(self.new_file)
        os.rmdir(self.new_file[:-16])

    def test_logger(self):
        test_log_dir = "/tmp/pyhole_log_test"
        log = utils.logger("TEST", test_log_dir, True)
        self.assertEqual("TEST", log.name)
        self.assertEqual(log.level, 0)
        os.unlink(test_log_dir + "/test.log")
        os.rmdir(test_log_dir)

    def test_decode_entities(self):
        test_str = "<foo>bar</foo>"
        self.assertEqual(utils.decode_entities(test_str), "bar")

    def test_decode_entities_2(self):
        test_str = "foo&nbsp;bar"
        self.assertEqual(utils.decode_entities(test_str), "foo bar")

    def test_decode_entities_3(self):
        test_str = "&amp;"
        self.assertEqual(utils.decode_entities(test_str), "&")

    def test_decode_entities_4(self):
        test_str = "&quot;"
        self.assertEqual(utils.decode_entities(test_str), "\"")

    def test_decode_entities_5(self):
        test_str = "&#8212;"
        self.assertEqual(utils.decode_entities(test_str), "-")

    def test_decode_entities_6(self):
        test_str = "&#8217;"
        self.assertEqual(utils.decode_entities(test_str), "'")

    def test_decode_entities_7(self):
        test_str = "&#8220;"
        self.assertEqual(utils.decode_entities(test_str), "\"")

    def test_decode_entities_8(self):
        test_str = "&#8221;"
        self.assertEqual(utils.decode_entities(test_str), "\"")

    def test_decode_entities_9(self):
        test_str = "&#8230;"
        self.assertEqual(utils.decode_entities(test_str), "...")

    def test_decode_entities_10(self):
        test_str = "<[lol^>"
        self.assertEqual(utils.decode_entities(test_str), "")

    def test_decode_entities_11(self):
        test_str = "<]*?>"
        self.assertEqual(utils.decode_entities(test_str), "")

    def test_decode_entities_12(self):
        test_str = "&#39;"
        self.assertEqual(utils.decode_entities(test_str), "'")

    def test_decode_entities_13(self):
        test_str = "&#x22;"
        self.assertEqual(utils.decode_entities(test_str), "\"")

    def test_decode_entities_14(self):
        test_str = "&#x27;"
        self.assertEqual(utils.decode_entities(test_str), "'")

    def test_decode_entities_15(self):
        test_str = "&#x26;"
        self.assertEqual(utils.decode_entities(test_str), "&")

    def test_decode_entities_16(self):
        test_str = "&ndash;"
        self.assertEqual(utils.decode_entities(test_str), "-")

    def test_decode_entities_17(self):
        test_str = "&#64;"
        self.assertEqual(utils.decode_entities(test_str), "@")

    def test_ensure_int(self):
        self.assertEqual(utils.ensure_int("3"), 3)

    def test_ensure_int_2(self):
        self.assertEqual(utils.ensure_int("\W"), None)

    def test_ensure_int_3(self):
        self.assertEqual(utils.ensure_int("a"), None)

    def test_load_config(self):
        test_config = utils.load_config("Pyhole", "../pyhole.conf.example")
        self.assertTrue(isinstance(test_config, object))

    def test_version(self):
        self.assertEqual(len(utils.version()), 41)

    def test_get_home_directory(self):
        self.assertTrue(utils.get_home_directory().endswith("/.pyhole/"))

    def test_get_directory(self):
        new_dir = utils.get_home_directory() + "test_dir"
        self.assertFalse(os.path.exists(new_dir))
        utils.get_directory("test_dir")
        self.assertTrue(os.path.exists(new_dir))
        os.rmdir(new_dir)

    def test_write_file(self):
        self.assertTrue(os.path.exists(self.new_file))

    def test_read_file(self):
        self.assertEquals(utils.read_file("tests", "pyhole_test_file"), "foo")
