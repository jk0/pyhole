#   Copyright 2010 Josh Kearney
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

"""Pyhole Utility Library"""


import re
import threading


def admin(func):
    """Administration Decorator"""

    def f(self, *args, **kwargs):
        if self.irc.source == self.irc.admin:
            func(self, *args, **kwargs)
        else:
            self.irc.say("Sorry, you are not authorized to do that.")
    f.__doc__ = func.__doc__
    return f


def spawn(func):
    """Thread Spawning Decorator"""

    def f(self, *args, **kwargs):
        if args and args[0]:
            params = " ".join(args)
            t = threading.Thread(
                target=func,
                args=(self, params),
                kwargs=kwargs)
        else:
            t = threading.Thread(target=func, args=(self,), kwargs=kwargs)
        self.irc.log.debug("Spawning: %s" % t.name)
        t.start()
    f.__doc__ = func.__doc__
    return f


def decode_entities(html):
    """Strip HTML entities from a string"""
    html = re.sub("<[^>]*?>", "", html)
    html = re.sub("&nbsp;", " ", html)
    html = re.sub("&quot;", "\"", html)
    html = re.sub("&#8212;", "-", html)
    html = re.sub("&#8217;", "'", html)
    html = re.sub("&#8220;", "\"", html)
    html = re.sub("&#8221;", "\"", html)
    html = re.sub("&#8230;", "...", html)

    return html.strip()
