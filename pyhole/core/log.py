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

import bz2
import glob
import logging
import logging.handlers
import os
import requests
import shutil

import utils


LOG_DIR = utils.get_directory("logs")
LOG_ARCHIVE_DIR = utils.get_directory(os.path.join("logs", "archive"))
LOG_FORMAT = "%(asctime)s [%(name)s] %(message)s"
LOG_DATEFMT = "%H:%M:%S"

class TimedRotatingCompressedFileHandler(logging.handlers.TimedRotatingFileHandler):
    def doRollover(self):
        result = super(TimedRotatingCompressedFileHandler, self).doRollover()

        # Compress uncompressed logs
        matcher = "*.log.*[!g][!z]"
        files = glob.glob(os.path.join(LOG_DIR, matcher))
        for filename in files:
            compressed_name = filename + ".bz2"
            with open(filename, 'rb') as input:
                with bz2.BZ2File(compressed_name, 'wb', compresslevel = 9) as output:
                    shutil.copyfileobj(input, output)

            basename = os.path.basename(filename)
            shutil.move(filename, os.path.join(LOG_ARCHIVE_DIR, basename))
            os.remove(filename)

        return result


def setup_logger(name="Pyhole"):
    """Log handler"""
    # NOTE(jk0): Disable unnecessary requests logging.
    requests.packages.urllib3.disable_warnings()
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    debug_option = utils.get_option("debug")
    debug_config = utils.get_config().get("debug", type="bool")
    debug = debug_option or debug_config

    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(level=log_level,
                        format=LOG_FORMAT,
                        datefmt=LOG_DATEFMT)

    log_file = os.path.join(LOG_DIR, name.lower() + ".log")
    log = TimedRotatingCompressedFileHandler(log_file, "midnight")
    log.setLevel(log_level)
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATEFMT)
    log.setFormatter(formatter)
    logging.getLogger(name).addHandler(log)


def get_logger(name="Pyhole"):
    return logging.getLogger(name)
