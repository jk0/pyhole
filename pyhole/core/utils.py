#   Copyright 2010-2016 Josh Kearney
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

"""Pyhole Utilies"""

import argparse
import datetime
import os
import re
import shutil
import threading

from BeautifulSoup import BeautifulStoneSoup

import config
import version


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
    """Thread-spawning decorator."""
    def wrap(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    wrap.__module__ = func.__module__

    return wrap


def decode_entities(html):
    """Strip HTML entities from a string and make it printable."""
    html = " ".join(str(x).strip() for x in BeautifulStoneSoup(html,
                    convertEntities=BeautifulStoneSoup.HTML_ENTITIES).findAll(
                    text=True))

    return filter(lambda x: ord(x) > 9 and ord(x) < 127, html)


def ensure_int(param):
    """Ensure the given param is an int."""
    try:
        param = re.sub("\W", "", param)
        return int(param)
    except ValueError:
        return None


def build_options():
    """Generate command line options."""
    parser = argparse.ArgumentParser(version=version.version_string())
    parser.add_argument("-c", "--config", default=get_conf_file_path(),
                        help="specify the path to a configuration file")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="show debugging output")

    return parser.parse_known_args()[0]


def get_option(option):
    """Retrive an option from the command line."""
    parsed_args = build_options()
    return vars(parsed_args).get(option)


def debug_enabled():
    """Return whether or not debug mode is enabled."""
    debug_option = get_option("debug")
    debug_config = get_config().get("debug", type="bool")
    return debug_option or debug_config


def get_home_directory():
    """Return the home directory."""
    home_dir = os.getenv("HOME") + "/.pyhole/"
    make_directory(home_dir)
    return home_dir


def get_directory(new_dir):
    """Return a directory."""
    home_dir = get_home_directory()
    new_dir = os.path.join(home_dir, new_dir, "")
    make_directory(new_dir)
    return new_dir


def make_directory(directory):
    """Make a direectory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_conf_file_path():
    """Return the path to the conf file."""
    return get_home_directory() + "pyhole.conf"


def get_conf_file():
    """Return the path to the conf file."""
    return get_option("config") or get_conf_file_path()


def get_config(section="Pyhole"):
    """Return the default config object."""
    return config.Config(get_conf_file(), section)


def write_file(directory, file_name, data):
    """Write data to file."""
    directory = get_directory(directory)
    with open(directory + file_name, "w") as open_file:
        open_file.write(str(data).strip())


def read_file(directory, file_name):
    """Read and return the data in file."""
    directory = get_directory(directory)
    try:
        with open(directory + file_name, "r") as open_file:
            data = open_file.read()
        return data
    except IOError:
        return None


def list_files(directory):
    """List files in a directory."""
    directory = get_directory(directory)
    return os.listdir(directory)


def prepare_config():
    """Prepare a sample configuration file."""
    conf_file = get_conf_file()
    if os.path.exists(conf_file):
        return

    try:
        print "Copying sample configuration file to: %s" % conf_file
        shutil.copyfile("pyhole.conf.sample", conf_file)
        print "Done. Please edit before running again."
    except IOError:
        # NOTE(jk0): Could not locate sample configuration file. This should
        # only happen when Read the Docs generates the documentation.
        pass


def datetime_now_string():
    """ISO 8601 formatted string of the current datetime."""
    return datetime.datetime.utcnow().isoformat()
