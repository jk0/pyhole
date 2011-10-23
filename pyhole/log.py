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


def get_logger(name="Pyhole"):
    """Log handler"""
    debug_option = utils.get_option("debug")
    debug_config = utils.get_config().get("debug", type="bool")
    debug = debug_option or debug_config

    log_dir = utils.get_directory("logs")
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s [%(name)s] %(message)s"
    log_datefmt = "%H:%M:%S"

    logging.basicConfig(level=log_level, format=log_format,
            datefmt=log_datefmt)

    log = logging.handlers.TimedRotatingFileHandler("%s/%s.log" % (log_dir,
            name.lower()), "midnight")
    log.setLevel(log_level)
    formatter = logging.Formatter(log_format, log_datefmt)
    log.setFormatter(formatter)
    logging.getLogger(name).addHandler(log)

    return logging.getLogger(name)
