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


class PyholeFileHandler(logging.handlers.TimedRotatingFileHandler):
    def doRollover(self):
        result = super(PyholeFileHandler, self).doRollover()
        self.archive_old_logs()
        return result

    def archive_old_logs(self):
        matcher = "*.log.*[!b][!z][!2]"
        files = glob.glob(os.path.join(LOG_DIR, matcher))
        for file_path in files:
            filename = os.path.basename(file_path)
            compressed_filename = filename + ".bz2"
            network_name = filename[:filename.rfind(".log")]
            archive_dir = os.path.join(LOG_ARCHIVE_DIR, network_name)
            utils.make_directory(archive_dir)
            compressed_file_path = os.path.join(archive_dir,
                                                compressed_filename)

            with open(file_path, "rb") as fp:
                with bz2.BZ2File(compressed_file_path, "wb",
                                 compresslevel=9) as output:
                    shutil.copyfileobj(fp, output)

            os.remove(file_path)


def setup_logger(name):
    """Setup the logger."""
    # NOTE(jk0): Disable unnecessary requests logging.
    requests.packages.urllib3.disable_warnings()
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.WARNING)

    debug = utils.debug_enabled()

    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(level=log_level,
                        format=LOG_FORMAT,
                        datefmt=LOG_DATEFMT)

    log_file = os.path.join(LOG_DIR, name.lower() + ".log")
    log = PyholeFileHandler(log_file, "midnight")
    log.setLevel(log_level)
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATEFMT)
    log.setFormatter(formatter)
    logging.getLogger(name).addHandler(log)

    log.archive_old_logs()


def get_logger(name="Pyhole"):
    return logging.getLogger(name)
