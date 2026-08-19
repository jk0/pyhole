# Copyright 2015-2026 Rick Harris and contributors
# SPDX-License-Identifier: Apache-2.0

"""Now-playing movies via TMDB (optional API key)."""

from __future__ import annotations

from pyhole.core import plugin, request, utils


class Boxoffice(plugin.Plugin):
    """Movies currently in theaters."""

    @plugin.hook_add_command("boxoffice")
    @utils.spawn
    def boxoffice(self, message, params=None, **kwargs):
        """Display movies currently in theaters."""
        key = utils.get_config("TMDB").get("key", default="")
        if not key:
            message.dispatch("No TMDB API key set. Add [TMDB] key=... to pyhole.conf.")
            return
        try:
            resp = request.get(
                "https://api.themoviedb.org/3/movie/now_playing",
                params={"api_key": key, "language": "en-US", "page": 1},
            )
            results = resp.json().get("results") or []
        except Exception:
            message.dispatch("Could not fetch box office results.")
            return
        if not results:
            message.dispatch("No now-playing results.")
            return
        message.dispatch("Now playing")
        for movie in results[:10]:
            title = movie.get("title", "Unknown")
            date = movie.get("release_date", "")
            score = movie.get("vote_average", "")
            message.dispatch(f"{title} ({date})  {score}")
