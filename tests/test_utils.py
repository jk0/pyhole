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

from __future__ import with_statement

import os
import sys
import unittest

from pyhole import utils


class TestUtils(unittest.TestCase):
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

    def test_ensure_int(self):
        self.assertEqual(utils.ensure_int("3"), 3)

    def test_ensure_int_2(self):
        self.assertEqual(utils.ensure_int("\W"), None)

    def test_ensure_int_3(self):
        self.assertEqual(utils.ensure_int("a"), None)

    def test_version(self):
        git_path = os.path.normpath(os.path.join(os.path.abspath(
                sys.argv[0]), os.pardir, os.pardir, ".git/refs/heads/master"))

        with open(git_path, "r") as git:
            git_commit = git.read()
        git.closed

        test_ver = "pyhole v0 (%s) - http://pyhole.org" % git_commit[0:5]
        self.assertEqual(utils.version("0"), test_ver)
