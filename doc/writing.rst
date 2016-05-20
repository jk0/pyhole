..
   Copyright 2011-2016 Josh Kearney

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Writing Pyhole Plugins
======================

The best way to learn how plugins work is by looking at real examples. You
can find them in the *pyhole.plugins* directory. Below you'll find a demo
that can be used as a template::

    #   Copyright <Year> <Your Name>
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

    """Pyhole Example Plugin"""

    from pyhole.core import plugin
    from pyhole.core import utils


    class Example(plugin.Plugin):
        """An example plugin."""

        @plugin.hook_add_command("test")
        @utils.require_params
        def test(self, message, params=None, **kwargs):
            """An example command (ex: .test foo)."""
            message.dispatch(params)

        @plugin.hook_add_keyword("t")
        @utils.require_params
        def keyword_t(self, message, params=None, **kwargs):
            """An example keyword (ex: T12345)."""
            if params:
                message.dispatch(params)

        @plugin.hook_add_msg_regex("(https?://|www.)[^\> ]+")
        def regex_match_url(self, message, match, **kwargs):
            """An example regex match."""
            message.dispatch(match.group(0))
