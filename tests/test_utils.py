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
import unittest

from pyhole.core import utils


class TestUtils(unittest.TestCase):
    def setUp(self):
        utils.write_file("tests", "pyhole_test_file", "foo")
        self.new_file = utils.get_home_directory() + "tests/pyhole_test_file"
        self.cpid = os.getpid()

    def tearDown(self):
        os.unlink(self.new_file)
        os.rmdir(self.new_file[:-16])

    def test_decode_entities(self):
        test_str = "<foo>&#64;&amp;bar&amp;&#64;</foo>"
        self.assertEqual(utils.decode_entities(test_str), "@&bar&@")

    def test_ensure_int(self):
        self.assertEqual(utils.ensure_int("3"), 3)

    def test_ensure_int_2(self):
        self.assertEqual(utils.ensure_int("\W"), None)

    def test_ensure_int_3(self):
        self.assertEqual(utils.ensure_int("a"), None)

    def test_build_options(self):
        options, _args = utils.build_options()
        self.assertTrue(isinstance(options, object))

    def test_get_option(self):
        conf_file = utils.get_option("config")
        self.assertTrue(conf_file.endswith("pyhole.conf"))

    def test_get_home_directory(self):
        self.assertTrue(utils.get_home_directory().endswith("/.pyhole/"))

    def test_get_directory(self):
        new_dir = utils.get_home_directory() + "test_dir"
        self.assertFalse(os.path.exists(new_dir))
        utils.get_directory("test_dir")
        self.assertTrue(os.path.exists(new_dir))
        os.rmdir(new_dir)

    def test_get_conf_file_path(self):
        conf_file_path = utils.get_conf_file_path()
        actual_conf_file_path = utils.get_home_directory() + "pyhole.conf"
        self.assertEqual(conf_file_path, actual_conf_file_path)

    def test_get_conf_file(self):
        actual_conf_file = utils.get_conf_file_path()
        generated_conf_file = utils.get_conf_file()
        self.assertEqual(actual_conf_file, generated_conf_file)

    def test_get_config(self):
        config = utils.get_config()
        debug = config.get("debug", type="bool")
        self.assertTrue(debug in [True, False])

    def test_write_file(self):
        self.assertTrue(os.path.exists(self.new_file))

    def test_read_file(self):
        self.assertEquals(utils.read_file("tests", "pyhole_test_file"), "foo")

    def test_subprocess(self):
        @utils.subprocess
        def test_pid():
            return os.getpid()

        self.assertNotEquals(self.cpid, test_pid())
