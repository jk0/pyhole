#   Copyright 2015-2016 Jason Meridth
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

"""Pyhole Stocks Plugin"""

import yahoo_finance

from pyhole.core import plugin
from pyhole.core import utils


class Stocks(plugin.Plugin):
    """Provide access to current stock values."""

    @plugin.hook_add_command("stock")
    @utils.require_params
    @utils.spawn
    def stocks(self, message, params=None, **kwargs):
        """Display current stock values (ex: .stock rax,yhoo,aapl)."""
        try:
            stocks = []
            symbols = params.upper().split(",")
            for symbol in symbols:
                share = yahoo_finance.Share(symbol)
                stocks.append("%s: %s (%s)" % (symbol, share.get_price(),
                                               share.get_change()))

            message.dispatch(", ".join(stocks))
        except Exception:
            message.dispatch("Unable to fetch stock data.")
