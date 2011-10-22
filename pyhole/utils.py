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
import os
import optparse
import re
import sys

from BeautifulSoup import BeautifulStoneSoup

import config
import version


eventlet.monkey_patch()


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
    """Strip HTML entities from a string and make it printable"""
    html = "".join(str(x).strip() for x in BeautifulStoneSoup(html,
            convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll(
            text=True))

    return filter(lambda x: ord(x) > 9 and ord(x) < 127, html)


def ensure_int(param):
    """Ensure the given param is an int"""
    try:
        param = re.sub("\W", "", param)
        return int(param)
    except ValueError:
        return None


def build_options():
    """Generate command line options"""
    default_conf_file = get_home_directory() + "pyhole.conf"

    parser = optparse.OptionParser(version=version.version_string())
    parser.add_option("-c", "--config", default=default_conf_file,
            help="specify the path to a configuration file")
    parser.add_option("-d", "--debug", action="store_true",
            help="show debugging output")

    return parser.parse_args()


def get_option(option):
    """Retrive an option from the command line."""
    options, args = build_options()
    return vars(options).get(option)


def get_home_directory():
    """Return the home directory"""
    home_dir = os.getenv("HOME") + "/.pyhole/"
    if not os.path.exists(home_dir):
        os.makedirs(home_dir)

    return home_dir


def get_directory(new_dir):
    """Return a directory"""
    home_dir = get_home_directory()
    new_dir = home_dir + new_dir

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    return new_dir + "/"


def get_conf_file():
    """Return the path to the conf file"""
    return get_option("config") or get_home_directory() + "pyhole.conf"


def get_config(section="Pyhole"):
    """Return the default config object"""
    return config.Config(get_conf_file(), section)


def write_file(dir, file, data):
    """Write data to file"""
    dir = get_directory(dir)

    with open(dir + file, "w") as f:
        f.write(str(data).strip())
    f.closed


def read_file(dir, file):
    """Read and return the data in file"""
    dir = get_directory(dir)

    try:
        with open(dir + file, "r") as f:
            data = f.read()
        f.closed

        return data
    except IOError:
        return None


def generate_config():
    """Generate an example config"""
    example = """# Global Configuration

[Pyhole]
admins: nick!ident, nick2!ident
command_prefix: .
reconnect_delay: 60
rejoin_delay: 5
debug: False
plugins: admin, dice, entertainment, news, search, urls, weather

[Redmine]
domain: redmine.example.com
key: abcd1234

# IRC Network Configuration

[FreeNode]
server: verne.freenode.net
password:
port: 7000
ssl: True
ipv6: True
bind_to: fe80::1
nick: mynick
identify_password: mypass
channels: #mychannel key, #mychannel2

[EFnet]
server: irc.efnet.net
password:
port: 6667
ssl: False
ipv6: False
bind_to:
nick: mynick
identify_password:
channels: #mychannel key, #mychannel2
"""

    conf_file = get_conf_file()
    if os.path.exists(conf_file):
        return

    print "Generating..."
    with open(conf_file, "w") as f:
        f.write(example)
    f.closed
    print "Done"
