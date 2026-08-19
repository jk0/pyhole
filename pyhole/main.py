# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""pyhole - A modular IRC and Slack bot."""

from __future__ import annotations

import sys
import time

from pyhole.core import api, config, logger, process, utils, version


def main(argv: list[str] | None = None) -> None:
    """Main loop."""
    args = utils.build_options(argv)
    utils.set_cli_args(args)

    if utils.prepare_config():
        sys.exit(0)

    try:
        conf = utils.get_config()
    except config.ConfigError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    logger.setup_logger("Pyhole")
    log = logger.get_logger()
    networks = conf.get("networks", type="list")

    log.info("Starting %s...", version.version_string())
    log.info("Connecting to networks: %s", ", ".join(networks))

    procs = []
    for network in networks:
        proc = process.Process(network)
        proc.start()
        procs.append(proc)

    try:
        if conf.get("api_enabled", type="bool", default=False):
            api.run()

        while True:
            time.sleep(1)
            procs = [proc for proc in procs if proc.is_alive()]
            if not procs:
                log.info("No longer connected to any networks; shutting down.")
                break
    except KeyboardInterrupt:
        log.info("Shutting down.")
    finally:
        for proc in procs:
            proc.terminate()
            proc.join(timeout=5)
