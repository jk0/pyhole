#   Copyright 2010-2011 Josh Kearney
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

import eventlet
import logging
import logging.handlers
import re
import string

from pyhole import config


eventlet.monkey_patch()

__CONFIG__ = "pyhole.cfg"


def logger(name, debug=False):
    """Log handler"""
    level = logging.DEBUG if debug else logging.INFO
    format = "%(asctime)s [%(name)s] %(message)s"
    datefmt = "%H:%M:%S"

    logging.basicConfig(level=level, format=format, datefmt=datefmt)

    log = logging.handlers.TimedRotatingFileHandler("logs/pyhole.log",
                                                    "midnight")
    log.setLevel(level)
    formatter = logging.Formatter(format, datefmt)
    log.setFormatter(formatter)
    logging.getLogger(name).addHandler(log)

    return logging.getLogger(name)


def admin(func):
    """Administration Decorator"""
    def f(self, *args, **kwargs):
        if self.irc.source in self.irc.admins:
            func(self, *args, **kwargs)
        else:
            self.irc.reply("Sorry, you are not authorized to do that.")
    f.__doc__ = func.__doc__
    f.__name__ = func.__name__
    f.__module__ = func.__module__
    return f


def spawn(func):
    """Greenthread Spawning Decorator"""
    def f(self, *args, **kwargs):
        eventlet.spawn_n(func, self, *args, **kwargs)
    f.__doc__ = func.__doc__
    f.__name__ = func.__name__
    f.__module__ = func.__module__
    return f


def decode_entities(html):
    """Strip HTML entities from a string"""
    html = re.sub("<[^>]*?>", "", html)
    html = re.sub("&nbsp;", " ", html)
    html = re.sub("&amp;", "&", html)
    html = re.sub("&quot;", "\"", html)
    html = re.sub("&#8212;", "-", html)
    html = re.sub("&#8217;", "'", html)
    html = re.sub("&#8220;", "\"", html)
    html = re.sub("&#8221;", "\"", html)
    html = re.sub("&#8230;", "...", html)
    html = filter(lambda x: x in string.printable, html)

    return html.strip()


def ensure_int(param):
    """Ensure the given param is an int"""
    try:
        param = re.sub("\W", "", param)
        return int(param)
    except ValueError:
        return None


def load_config(section):
    """Load a config section"""
    return config.Config(__CONFIG__, section)
