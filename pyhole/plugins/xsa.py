# Copyright 2015-2026 Rick Harris and contributors
# SPDX-License-Identifier: Apache-2.0

"""Xen Security Advisory plugin."""

from __future__ import annotations

import json

from bs4 import BeautifulSoup

from pyhole.core import plugin, request, utils


class Xsa(plugin.Plugin):
    """Xen Security Advisories."""

    XSA_URL = "https://xenbits.xen.org/xsa/"

    @plugin.hook_add_keyword("xsa")
    @utils.require_params
    @utils.spawn
    def keyword_xsa(self, message, params=None, **kwargs):
        """Retrieve XSA information (ex: xsa123 or xsa-123)."""
        xsa_num = abs(utils.ensure_int(params) or 0)
        xsa_id = f"XSA-{xsa_num}"
        msg = self._make_xsa_message(xsa_id, self._load_cached_xsa_data())
        message.dispatch(msg or "Unable to find matching XSA.")

    def _make_xsa_message(self, xsa_id: str, data: dict) -> str | None:
        info = data.get(xsa_id)
        if not info:
            return None
        if not info.get("link"):
            info = {**info, "link": info.get("id")}
        return f"{info['link']}: {info['title']} (Public Release: {info['public_release']})"

    @plugin.hook_add_poll("poll_xsa_list", poll_timer=300)
    def poll_xsa_list(self, message, params=None, **kwargs):
        old_data = self._load_cached_xsa_data()
        new_data = self._fetch_xsa_data()
        if not new_data:
            return
        utils.write_file(self.name, "xsas.json", json.dumps(new_data))
        old_ids = set(old_data)
        added = set(new_data) - old_ids
        if old_ids and added:
            self._notify_new_xsas(added, new_data)

    def _notify_new_xsas(self, added_xsa_ids, new_data) -> None:
        notify_str = utils.get_config("XSA").get("notify", default="")
        if not notify_str:
            return
        channels = [item.strip() for item in notify_str.split(",") if item.strip()]
        for xsa_id in added_xsa_ids:
            msg = self._make_xsa_message(xsa_id, new_data)
            if not msg:
                continue
            for channel in channels:
                self.session.notice(channel, msg)

    def _load_cached_xsa_data(self) -> dict:
        data_json = utils.read_file(self.name, "xsas.json")
        if data_json is None:
            return {}
        try:
            return json.loads(data_json)
        except json.JSONDecodeError:
            return {}

    def _fetch_xsa_data(self) -> dict:
        try:
            resp = request.get(self.XSA_URL)
        except Exception:
            return {}
        if resp.status_code != 200:
            return {}
        soup = BeautifulSoup(resp.text, "html.parser")
        data: dict = {}
        for row in soup.find_all("tr"):
            children = row.find_all("td")
            if not children:
                continue
            try:
                xsa_id = children[0].get_text(strip=True)
            except Exception:
                continue
            link = None
            anchor = children[0].find("a")
            if anchor and anchor.get("href"):
                link = self.XSA_URL + anchor["href"]
            public_release = children[1].get_text(strip=True) if len(children) > 1 else None
            title = children[5].get_text(strip=True) if len(children) > 5 else None
            data[xsa_id] = {
                "id": xsa_id,
                "link": link,
                "public_release": public_release,
                "title": title,
            }
        return data
