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

"""Pyhole Logging"""

import logging
import logging.handlers

import utils


def getLogger(name="Pyhole"):
    """Log handler"""
    debug_option = utils.get_option("debug")
    debug_config = utils.get_config().get("debug", type="bool")
    debug = debug_option or debug_config

    log_dir = utils.get_directory("logs")
    level = logging.DEBUG if debug else logging.INFO
    format = "%(asctime)s [%(name)s] %(message)s"
    datefmt = "%H:%M:%S"

    logging.basicConfig(level=level, format=format, datefmt=datefmt)

    log = logging.handlers.TimedRotatingFileHandler("%s/%s.log" % (log_dir,
            name.lower()), "midnight")
    log.setLevel(level)
    formatter = logging.Formatter(format, datefmt)
    log.setFormatter(formatter)
    logging.getLogger(name).addHandler(log)

    return logging.getLogger(name)
