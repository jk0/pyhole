# Copyright 2015-2026 Jason Meridth, Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

"""Stock quotes via Yahoo Finance's public chart API."""

from __future__ import annotations

from pyhole.core import plugin, request, utils

_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


class Stocks(plugin.Plugin):
    """Current stock values."""

    @plugin.hook_add_command("stock")
    @utils.require_params
    @utils.spawn
    def stocks(self, message, params=None, **kwargs):
        """Display current stock values (ex: .stock rax,yhoo,aapl)."""
        quotes = []
        for raw in params.split(","):
            symbol = raw.strip().upper()
            if not symbol:
                continue
            try:
                resp = request.get(
                    _CHART.format(symbol=symbol),
                    params={"range": "1d", "interval": "1d"},
                )
                meta = resp.json()["chart"]["result"][0]["meta"]
                price = meta.get("regularMarketPrice")
                previous = meta.get("chartPreviousClose") or meta.get("previousClose")
                if price is None:
                    quotes.append(f"{symbol}: n/a")
                    continue
                change = ""
                if previous:
                    delta = price - previous
                    change = f" ({delta:+.2f})"
                quotes.append(f"{symbol}: {price}{change}")
            except Exception:
                quotes.append(f"{symbol}: error")

        if not quotes:
            message.dispatch("Unable to fetch stock data.")
            return
        message.dispatch(", ".join(quotes))
