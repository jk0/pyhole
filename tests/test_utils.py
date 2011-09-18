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
        test_log_dir = utils.get_home_directory() + "logs/"
        log = utils.logger("TEST", True)
        self.assertEqual("TEST", log.name)
        self.assertEqual(log.level, 0)
        os.unlink(test_log_dir + "test.log")

    def test_decode_entities(self):
        test_str = "<foo>&#64;&amp;bar&amp;&#64;</foo>"
        self.assertEqual(utils.decode_entities(test_str), "@&bar&@")

    def test_ensure_int(self):
        self.assertEqual(utils.ensure_int("3"), 3)

    def test_ensure_int_2(self):
        self.assertEqual(utils.ensure_int("\W"), None)

    def test_ensure_int_3(self):
        self.assertEqual(utils.ensure_int("a"), None)

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
