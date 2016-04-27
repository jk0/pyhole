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

"""Pyhole Version Unit Tests"""

import unittest

from pyhole.core import version


class TestVersion(unittest.TestCase):
    def test_current_git_hash(self):
        self.assertEqual(len(version.current_git_hash()), 5)

    def test_version_string(self):
        self.assertTrue(version.version_string().startswith("pyhole v"))

    def test_version_hash(self):
        self.assertEqual(len(version.version_hash()), 12)

    def test_version(self):
        self.assertEqual(len(version.version()), 6)
