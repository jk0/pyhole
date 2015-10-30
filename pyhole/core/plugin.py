#   Copyright 2011-2015 Chris Behrens
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

"""Pyhole Plugin Library"""

import functools
import os
import re
import sys
import time

import log
import utils


LOG = log.get_logger()

_plugin_instances = []
_plugin_hooks = {}


def _reset_variables():
    """Local function to init some variables that are common between
    load and reload
    """
    global _plugin_instances
    global _plugin_hooks

    _plugin_instances = []
    _plugin_hooks = {}

    for x in _hook_names:
        _plugin_hooks[x] = []


def hook_add(hookname, arg, poll_timer=60):
    """Generic decorator to add hooks.  Generally, this is not called
    directly by plugins.  Decorators that plugins use are automatically
    generated below with the setattrs you'll see
    """
    def wrap(f):
        if hookname == "poll":
            @utils.spawn
            def _f(self, *args, **kwargs):
                while True:
                    f(self, *args, **kwargs)
                    time.sleep(poll_timer)

            setattr(_f, "_is_%s_hook" % hookname, True)
            _f._hook_arg = arg

            return _f
        else:
            setattr(f, "_is_%s_hook" % hookname, True)
            f._hook_arg = arg

            return f

    return wrap


def hook_get(hookname):
    """Function to return the list of hooks of a particular type.  Genearlly
    this is not called directly.  Callers tend to use the dynamically
    generated calls 'hook_get_*' that are created below with the setattrs
    """
    return _plugin_hooks[hookname]


def active_get(hookname):
    """Function to return the list of hook arguments.  Genearlly
    this is not called directly.  Callers tend to use the dynamically
    generated calls 'active_get_*' that are created below with the
    setattrs
    """
    return ", ".join(sorted([x[2] for x in _plugin_hooks[hookname]]))


_hook_names = ["keyword", "command", "msg_regex", "poll"]
_reset_variables()
_this_mod = sys.modules[__name__]


for x in _hook_names:
    # Dynamically create the decorators and functions for various hooks
    setattr(_this_mod, "hook_add_%s" % x, functools.partial(hook_add, x))
    setattr(_this_mod, "hook_get_%ss" % x, functools.partial(hook_get, x))
    setattr(_this_mod, "active_%ss" % x, functools.partial(active_get, x))


class PluginMetaClass(type):
    """The metaclass that makes all of the plugin magic work.  All subclassing
    gets caught here, which we can use to have plugins automagically
    register themselves
    """

    def __init__(cls, name, bases, attrs):
        """Catch subclassing.  If the class doesn't yet have _plugin_classes,
        it means it's the Plugin class itself, otherwise it's a class
        that's been subclassed from Plugin (ie, a real plugin class)
        """
        if not hasattr(cls, "_plugin_classes"):
            cls._plugin_classes = []
        else:
            cls._plugin_classes.append(cls)
        cls.__name__ = name


class Plugin(object):
    """The class that all plugin classes should inherit from"""
    __metaclass__ = PluginMetaClass

    def __init__(self, session, *args, **kwargs):
        """Default constructor for Plugin. Stores the client instance, etc"""
        self.session = session
        self.name = self.__class__.__name__


def _init_plugins(*args, **kwargs):
    """Create instances of the plugin classes and create a cache
    of their hook functions
    """
    for cls in Plugin._plugin_classes:
        # Create instance of 'p'
        instance = cls(*args, **kwargs)
        # Store the instance
        _plugin_instances.append(instance)

        # Setup _keyword_hooks by looking at all of the attributes
        # in the class and finding the ones that have a _is_*_hook
        # attribute
        for attr_name in dir(instance):
            attr = getattr(instance, attr_name)

            for hook_key in _hook_names:
                if getattr(attr, "_is_%s_hook" % hook_key, False):
                    hook_arg = getattr(attr, "_hook_arg", None)
                    # Append (module, method, arg) tuple
                    _plugin_hooks[hook_key].append((attr.__module__, attr,
                                                    hook_arg))


def load_user_plugin(plugin, *args, **kwargs):
    """Load a user plugin"""
    sys.path.append(utils.get_home_directory() + "plugins")
    user_plugins = os.listdir(utils.get_directory("plugins"))

    for user_plugin in user_plugins:
        if user_plugin.endswith(".py"):
            user_plugin = user_plugin[:-3]
            if plugin == user_plugin:
                try:
                    __import__(plugin, globals(), locals(), [plugin])
                except Exception, exc:
                    LOG.error(exc)


def load_plugins(*args, **kwargs):
    """Module function that loads plugins from a particular directory"""
    config = utils.get_config()
    plugin_names = config.get("plugins", type="list")

    for plugin_name in plugin_names:
        load_user_plugin(plugin_name, *args, **kwargs)

        try:
            __import__("pyhole.plugins", globals(), locals(), [plugin_name])
        except Exception, exc:
            LOG.error(exc)

    _init_plugins(*args, **kwargs)


def reload_plugins(*args, **kwargs):
    """Module function that'll reload all of the plugins"""
    config = utils.get_config()

    # Terminate running poll instances
    for plugin in _plugin_instances:
        for attr_name in dir(plugin):
            attr = getattr(plugin, attr_name)
            if getattr(attr, "_is_poll_hook", False):
                # TODO(jk0): Doing this kills the entire process. We need to
                # figure out how to kill it properly. Until this is done,
                # reloading will not work with polls.
                # attr().throw(KeyboardInterrupt)
                pass

    # When the modules are reloaded, the meta class will append
    # all of the classes again, so we need to make sure this is empty
    Plugin._plugin_classes = []
    _reset_variables()

    # Now reload all of the plugins
    plugins_to_reload = []
    plugindir = "pyhole.plugins"
    local_plugin_dir = utils.get_home_directory() + "plugins"

    # Reload existing plugins
    for mod, val in sys.modules.items():
        if plugindir in mod and val and mod != plugindir:
            mod_file = val.__file__
            if not os.path.isfile(mod_file):
                continue
            for p in config.get("plugins", type="list"):
                if plugindir + "." + p == mod:
                    plugins_to_reload.append(mod)

        if local_plugin_dir in str(val):
            plugins_to_reload.append(mod)

    for plugin in plugins_to_reload:
        try:
            reload(sys.modules[plugin])
        except Exception, exc:
            LOG.error(exc)

    # Load new plugins
    load_plugins(*args, **kwargs)


def active_plugins():
    """Get the loaded plugin names"""
    return ", ".join(sorted([x.__name__ for x in Plugin._plugin_classes]))


def active_plugin_classes():
    """Get the loaded plugin classes"""
    return Plugin._plugin_classes


def run_hook_command(session, mod_name, func, message, arg, **kwargs):
    """Make a call to a plugin hook."""
    try:
        if arg:
            session.log.debug("Calling: %s.%s(\"%s\")" % (mod_name,
                              func.__name__, arg))
        else:
            session.log.debug("Calling: %s.%s(None)" % (mod_name,
                              func.__name__))
        func(message, arg, **kwargs)
    except Exception, exc:
        session.log.exception(exc)


def run_hook_polls(session):
    """Run polls in the background."""
    message = None
    for mod_name, func, cmd in hook_get_polls():
        run_hook_command(session, mod_name, func, message, cmd)


def run_msg_regexp_hooks(session, message, private):
    """Run regexp hooks."""
    msg = message.message
    for mod_name, func, msg_regex in hook_get_msg_regexs():
        match = re.search(msg_regex, msg, re.I)
        if match:
            run_hook_command(session, mod_name, func, message, match,
                             private=private)


def run_keyword_hooks(session, message, private):
    """Run keyword hooks."""
    msg = message.message
    words = msg.split(" ")
    for mod_name, func, kwarg in hook_get_keywords():
        for word in words:
            match = re.search("^%s(.+)" % kwarg, word, re.I)
            if match:
                run_hook_command(session, mod_name, func, message,
                                 match.group(1), private=private)


def run_command_hooks(session, message, private):
    """Run command hooks."""
    msg = message.message
    for mod_name, func, cmd in hook_get_commands():
        session.addressed = False

        if private:
            match = re.search("^%s$|^%s\s(.*)$" % (cmd, cmd), msg,
                              re.I)
            if match:
                run_hook_command(session, mod_name, func, message,
                                 match.group(1), private=private,
                                 addressed=session.addressed)

        if msg.startswith(session.command_prefix):
            # Strip off command prefix
            msg_rest = msg[len(session.command_prefix):]
        else:
            # Check for command starting with nick being addressed
            msg_start_upper = msg[:len(session.nick) + 1].upper()
            if msg_start_upper == session.nick.upper() + ":":
                # Get rest of string after "nick:" and white spaces
                msg_rest = re.sub("^\s+", "",
                                  msg[len(session.nick) + 1:])
            else:
                continue

            session.addressed = True

        match = re.search("^%s$|^%s\s(.*)$" % (cmd, cmd), msg_rest, re.I)
        if match:
            run_hook_command(session, mod_name, func, message, match.group(1),
                             private=private,
                             addressed=session.addressed)


def poll_messages(session, message, private=False):
    """Watch for known commands."""
    session.addressed = False

    run_command_hooks(session, message, private)
    run_keyword_hooks(session, message, private)
    run_msg_regexp_hooks(session, message, private)
