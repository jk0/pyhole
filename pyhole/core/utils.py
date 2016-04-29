#   Copyright 2010-2015 Josh Kearney
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
import optparse
import os
import re
import requests
import sys
import traceback

from BeautifulSoup import BeautifulStoneSoup
from functools import wraps
from multiprocessing import Process
from multiprocessing import Queue

import config
import version


eventlet.monkey_patch()


def admin(func):
    """Require admin rights."""
    def wrap(self, message, *args, **kwargs):
        if message.source in self.session.admins:
            return func(self, message, *args, **kwargs)

        return message.dispatch("Sorry, you are not authorized to do that.")

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    wrap.__module__ = func.__module__

    return wrap


def require_params(func):
    """Require parameters."""
    def wrap(self, message, params, *args, **kwargs):
        if not params:
            message.dispatch(wrap.__doc__)
            return

        return func(self, message, params, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    wrap.__module__ = func.__module__

    return wrap


def spawn(func):
    """Greenthread Spawning Decorator"""
    def wrap(self, *args, **kwargs):
        eventlet.spawn_n(func, self, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    wrap.__module__ = func.__module__

    return wrap


def subprocess(func):
    """Decorator running function in subprocess."""
    def _subprocess(q, *args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except Exception:
            ex_type, ex_value, tb = sys.exc_info()
            error = ex_type, ex_value, "".join(traceback.format_tb(tb))
            ret = None
        else:
            error = None

        q.put((ret, error))

    @wraps(func)
    def wrapper(*args, **kwargs):
        q = Queue()
        p = Process(target=_subprocess, args=[q] + list(args), kwargs=kwargs)
        p.start()
        p.join()
        ret, error = q.get()

        if error:
            ex_type, ex_value, tb_str = error
            message = "%s (in subprocess)\n%s" % (ex_value.message, tb_str)
            raise ex_type(message)

        return ret

    return wrapper


def decode_entities(html):
    """Strip HTML entities from a string and make it printable"""
    html = re.sub("\n", "", html)
    html = re.sub(" +", " ", html)
    html = " ".join(str(x).strip() for x in BeautifulStoneSoup(html,
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
    parser = optparse.OptionParser(version=version.version_string())
    parser.add_option("-c", "--config", default=get_conf_file_path(),
                      help="specify the path to a configuration file")
    parser.add_option("-d", "--debug", action="store_true",
                      help="show debugging output")

    return parser.parse_args()


def get_option(option):
    """Retrive an option from the command line."""
    options, _args = build_options()

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


def get_conf_file_path():
    """Return the path to the conf file"""
    return get_home_directory() + "pyhole.conf"


def get_conf_file():
    """Return the path to the conf file"""
    return get_option("config") or get_conf_file_path()


def get_config(section="Pyhole"):
    """Return the default config object"""
    return config.Config(get_conf_file(), section)


def write_file(directory, file_name, data):
    """Write data to file"""
    directory = get_directory(directory)
    with open(directory + file_name, "w") as open_file:
        open_file.write(str(data).strip())


def read_file(directory, file_name):
    """Read and return the data in file"""
    directory = get_directory(directory)
    try:
        with open(directory + file_name, "r") as open_file:
            data = open_file.read()

        return data
    except IOError:
        return None


def list_files(directory):
    directory = get_directory(directory)

    return os.listdir(directory)


def generate_config():
    """Generate an example config"""
    example = """# Global Configuration

[Pyhole]
admins = nick!ident, nick2!ident, slack.username
command_prefix = .
reconnect_delay = 60
rejoin_delay = 5
debug = False
plugins = admin
networks = FreeNode, EFnet, SlackNetwork

[GoogleMaps]
key = abcd1234

[Jira]
auth_server = auth.jira.example.com
domain = jira.example.com
username = abcd1234
password = pass1234

[PagerDuty]
subdomain = https://subdomain.pagerduty.com
key = abcd1234

[Redmine]
domain = redmine.example.com
key = abcd1234

[Wunderground]
key = abcd1234

[XSA]
notify = #channel1, #channel2

# Network Configuration

[FreeNode]
server = verne.freenode.net
username =
password =
port = 7000
ssl = True
ipv6 = True
bind_to = fe80::1
nick = mynick
identify_password = abcd1234
channels = #mychannel key, #mychannel2

[EFnet]
server = irc.efnet.net
username =
password =
port = 6667
ssl = False
ipv6 = False
bind_to =
nick = mynick
identify_password =
channels = #mychannel key, #mychannel2

[SlackNetwork]
api_token = abcd1234
nick = mynick
"""

    conf_file = get_conf_file()
    if os.path.exists(conf_file):
        return

    print "Generating..."
    with open(conf_file, "w") as open_file:
        open_file.write(example)
    print "Done"


def fetch_url(url, **kwargs):
    """Fetch a URL."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "pyhole/%s" % version.version()
    })
    return session.get(url, **kwargs)
