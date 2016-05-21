#   Copyright 2011-2016 Josh Kearney
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

"""Pyhole Log Unit Tests"""

import os
import unittest

from pyhole.core import logger
from pyhole.core import utils


class TestLogger(unittest.TestCase):
    def test_logger(self):
        test_log_dir = utils.get_home_directory() + "logs/"

        try:
            # NOTE(jk0): If the configuration file doesn't exist, the config
            # class will generate it and raise a SystemExit.
            logger.setup_logger("test")
        except SystemExit:
            logger.setup_logger("test")

        test_log = logger.get_logger("TEST")

        self.assertEqual("TEST", test_log.name)
        self.assertEqual(test_log.level, 0)

        os.unlink(test_log_dir + "test.log")
