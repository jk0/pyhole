# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pyhole logging."""

from __future__ import annotations

import bz2
import glob
import logging
import logging.handlers
import os
import shutil
from pathlib import Path

from pyhole.core import utils

LOG_FORMAT = "%(asctime)s [%(name)s] %(message)s"
LOG_DATEFMT = "%H:%M:%S"


class PyholeFileHandler(logging.handlers.TimedRotatingFileHandler):
    def doRollover(self) -> None:
        super().doRollover()
        self.archive_old_logs()

    def archive_old_logs(self) -> None:
        log_dir = utils.get_directory("logs")
        archive_root = utils.get_directory(os.path.join("logs", "archive"))
        matcher = "*.log.*[!b][!z][!2]"
        for file_path in glob.glob(str(log_dir / matcher)):
            path = Path(file_path)
            compressed_filename = path.name + ".bz2"
            network_name = path.name[: path.name.rfind(".log")]
            archive_dir = archive_root / network_name
            utils.make_directory(archive_dir)
            compressed_file_path = archive_dir / compressed_filename
            with (
                path.open("rb") as fp,
                bz2.BZ2File(compressed_file_path, "wb", compresslevel=9) as output,
            ):
                shutil.copyfileobj(fp, output)
            path.unlink()


def setup_logger(name: str) -> None:
    """Setup the logger for a network (or the process)."""
    debug = utils.debug_enabled()
    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(level=log_level, format=LOG_FORMAT, datefmt=LOG_DATEFMT)

    log_file = utils.get_directory("logs") / f"{name.lower()}.log"
    handler = PyholeFileHandler(log_file, when="midnight", encoding="utf-8")
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATEFMT))
    logging.getLogger(name).addHandler(handler)
    handler.archive_old_logs()


def get_logger(name: str = "Pyhole") -> logging.Logger:
    return logging.getLogger(name)
