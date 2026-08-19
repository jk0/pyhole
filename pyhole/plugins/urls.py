# Copyright 2011-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""URL title plugin."""

from __future__ import annotations

from bs4 import BeautifulSoup

from pyhole.core import plugin, request, utils

_LOOKUP_HOSTS = ("open.spotify.com", "www.youtube.com", "youtu.be")


class Url(plugin.Plugin):
    """URL titles."""

    def __init__(self, session):
        super().__init__(session)
        self.url = None

    @plugin.hook_add_command("title")
    def title(self, message, params=None, **kwargs):
        """Display the title of a URL (ex: .title [<url>])."""
        if params:
            self.url = params.split(" ", 1)[0]
        if self.url and not _matches_host(self.url):
            self._find_title(message, self.url)

    @plugin.hook_add_msg_regex(r"(https?://|www\.)[^\> ]+")
    def regex_match_url(self, message, match, **kwargs):
        """Watch and keep track of the latest URL."""
        try:
            self.url = match.group(0).split("|", 1)[0]
            if _matches_host(self.url):
                self._find_title(message, self.url)
        except (TypeError, AttributeError):
            return

    @utils.spawn
    def _find_title(self, message, url):
        url = url.replace("<", "").replace(">", "").split("|")[0]
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        try:
            response = request.get(url)
        except Exception:
            return
        soup = BeautifulSoup(response.content, "html.parser")
        if soup.title and soup.title.string:
            title = utils.decode_entities(soup.title.string)
            content_type = response.headers.get("Content-Type", "")
            message.dispatch(f"{title} ({content_type})")
        else:
            message.dispatch(f"No title found: {url}")


def _matches_host(url: str | None) -> bool:
    if not url:
        return False
    try:
        host = url.split("/")[2]
    except IndexError:
        host = url
    return host.startswith(_LOOKUP_HOSTS)
