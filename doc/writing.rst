..
   Copyright 2011-2026 Josh Kearney

Writing Pyhole Plugins
======================

Plugin hook names are unchanged from classic pyhole. Look at
``pyhole/plugins`` for real examples. A minimal plugin::

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

        @plugin.hook_add_msg_regex(r"(https?://|www\.)[^\> ]+")
        def regex_match_url(self, message, match, **kwargs):
            """An example regex match."""
            message.dispatch(match.group(0))

Drop the file in ``pyhole/plugins/`` or ``~/.pyhole/plugins/`` and add the
module name to the ``plugins`` list in ``pyhole.conf``.
