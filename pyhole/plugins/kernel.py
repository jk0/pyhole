# Copyright 2011-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Kernel.org plugin."""

from __future__ import annotations

import re

from pyhole.core import plugin, request, utils


class Kernel(plugin.Plugin):
    """kernel.org data."""

    @plugin.hook_add_command("kernel")
    @utils.spawn
    def kernel(self, message, params=None, **kwargs):
        """Retrieve the current kernel version (ex: .kernel)."""
        try:
            response = request.get("https://www.kernel.org/kdist/finger_banner")
        except Exception:
            return
        if response.status_code != 200:
            return
        match = re.search(r"(.* mainline .*)", response.text)
        if not match:
            return
        kernel = re.sub(r" {2,}", " ", match.group(1)).strip()
        message.dispatch(kernel)
