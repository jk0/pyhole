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

"""Pyhole Unit Tests"""

import os
import sys

from nose import config
from nose import core


if __name__ == "__main__":
    tests = os.path.abspath(os.path.join("tests"))
    tests_config = config.Config(stream=sys.stdout, env=os.environ,
            verbosity=3, workingDir=tests, plugins=core.DefaultPluginManager())
    core.run(config=tests_config, argv=sys.argv)
