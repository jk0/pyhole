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

from __future__ import with_statement

import eventlet
import logging
import logging.handlers
import os
import re
import sys

from pyhole import config


eventlet.monkey_patch()


def logger(name, log_dir, debug=False):
    """Log handler"""
    level = logging.DEBUG if debug else logging.INFO
    format = "%(asctime)s [%(name)s] %(message)s"
    datefmt = "%H:%M:%S"

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(level=level, format=format, datefmt=datefmt)

    log = logging.handlers.TimedRotatingFileHandler("%s/pyhole.log" % log_dir,
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
    entities = [
        ("<[^>]*?>", ""),
        ("&nbsp;", " "),
        ("&amp;", "&"),
        ("&quot;", "\""),
        ("&#8212;", "-"),
        ("&#8217;", "'"),
        ("&#39;", "'"),
        ("&#8220;", "\""),
        ("&#8221;", "\""),
        ("&#8230;", "..."),
        ("&#x22;", "\""),
        ("&#x27;", "'")]

    html = reduce(lambda a, b: re.sub(b[0], b[1], a), entities, html)
    return filter(lambda x: ord(x) > 9 and ord(x) < 127, html).strip()


def ensure_int(param):
    """Ensure the given param is an int"""
    try:
        param = re.sub("\W", "", param)
        return int(param)
    except ValueError:
        return None


def load_config(section, conf):
    """Load a config section"""
    return config.Config(conf, section)


def version(number):
    """Prepare the version string"""
    git_path = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
            os.pardir, os.pardir, ".git/refs/heads/master"))

    if not os.path.exists(git_path):
        return "pyhole v%s - http://pyhole.org" % number

    with open(git_path, "r") as git:
        git_commit = git.read()
    git.closed

    return "pyhole v%s (%s) - http://pyhole.org" % (number, git_commit[0:5])
