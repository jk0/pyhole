# Copyright 2010-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Search plugins (Urban Dictionary JSON API + Wikipedia OpenSearch)."""

from __future__ import annotations

from pyhole.core import plugin, request, utils


class Search(plugin.Plugin):
    """Search engines."""

    @plugin.hook_add_command("urban")
    @utils.require_params
    @utils.spawn
    def urban(self, message, params=None, **kwargs):
        """Search Urban Dictionary (ex: .urban <query>)."""
        try:
            resp = request.get(
                "https://api.urbandictionary.com/v0/define",
                params={"term": params},
            )
            listing = (resp.json().get("list") or [None])[0]
        except Exception:
            message.dispatch(f"No results found: '{params}'")
            return
        if not listing:
            message.dispatch(f"No results found: '{params}'")
            return
        meaning = utils.decode_entities(listing.get("definition") or "")
        example = utils.decode_entities(listing.get("example") or "")
        if example:
            message.dispatch(f"{meaning} (ex: {example})")
        else:
            message.dispatch(meaning)

    @plugin.hook_add_command("wikipedia")
    @utils.require_params
    @utils.spawn
    def wikipedia(self, message, params=None, **kwargs):
        """Search Wikipedia (ex: .wikipedia <query>)."""
        try:
            resp = request.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "opensearch",
                    "search": params,
                    "limit": 4,
                    "namespace": 0,
                    "format": "json",
                },
            )
            data = resp.json()
            urls = data[3] if len(data) > 3 else []
        except Exception:
            return
        if not urls:
            message.dispatch(f"No results found: '{params}'")
            return
        for url in urls:
            message.dispatch(url)
