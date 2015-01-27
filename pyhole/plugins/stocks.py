#   Copyright 2010-2012 Josh Kearney
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

from pyhole.core import plugin, utils
from yahoo_finance import Share


class Stocks(plugin.Plugin):
    """Provide access to current stock values"""

    @plugin.hook_add_command("stock")
    @utils.spawn
    def stocks(self, message, params=None, **kwargs):
        """Display current stock value for user provided symbol(s)
        (ex: .stock rax,yhoo,aapl)
        """

        if not params:
            message.dispatch("No stock symbol provided, please provide "
                             "at least one symbol. Example: .stock rax or "
                             ".stock rax,yhoo,aapl")
            return

        text = ""
        try:
            symbols = params.upper().split(',')
            for s in symbols:
                share = Share(s)
                text = (text + "%s: %s (%s) | " %
                        (s, share.get_price(), share.get_change()))
            text = text.rstrip(" ")
            text = text.rstrip("|")
        except Exception:
            text = ("Unable to fetch stocks data. "
                    "Please ensure the symbols you've provided are valid")

        message.dispatch(text)
