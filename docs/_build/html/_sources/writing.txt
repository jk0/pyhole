..
   Copyright 2011 Josh Kearney

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Writing Plugins
===============

The best way to learn how plugins work is by looking at real examples. You
can find them in the *plugins* directory. Below you'll find a demo that can be
used as a template::

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

    from pyhole import plugin


    class Example(plugin.Plugin):
        """An example plugin"""

        @plugin.hook_add_command("test")
        def test(self, params=None, **kwargs):
            """An example command (ex: .test foo)"""
            if params:
                self.irc.reply(params)
            else:
                self.irc.reply(self.test.__doc__)

        @plugin.hook_add_keyword("t")
        def keyword_t(self, params=None, **kwargs):
            """An example keyword (ex: T12345)"""
            if params:
                self.irc.reply(params)

        @plugin.hook_add_msg_regex("https?:\/\/")
        def _watch_for_url(self, params=None, **kwargs):
            """An example regex match"""
            try:
                url = kwargs["full_message"].split(" ", 1)[0]
                self.irc.reply(url)
            except TypeError:
                return
