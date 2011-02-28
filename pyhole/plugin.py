# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#   Copyright 2011 Chris Behrens
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
import re
import sys

def _reset_variables():
    global _plugin_instances
    global _plugin_hooks
    _plugin_instances = []
    _plugin_hooks = {}
    for x in _hook_names:
        _plugin_hooks[x] = []

# Decorator for adding a hook
def hook_add(hookname, arg):
    def wrap(f):
        setattr(f, '_is_%s_hook' % hookname, True)
        f._hook_arg = arg
        return f
    return wrap

def hook_get(hookname):
    return _plugin_hooks[hookname]

def active_get(hookname):
    return [x[2] for x in _plugin_hooks[hookname]]

_plugins = []
_plugins_module = None
_hook_names = ['keyword', 'command', 'msg_regex']
_reset_variables()
_this_mod = sys.modules[__name__]

for x in _hook_names:
    # Dynamically create the decorators for various hooks
    setattr(_this_mod, "hook_add_%s" % x, functools.partial(hook_add, x))
    setattr(_this_mod, "hook_get_%ss" % x, functools.partial(hook_get, x))
    setattr(_this_mod, "active_%ss" % x, functools.partial(active_get, x))


class PluginMetaClass(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, '_plugin_classes'):
            cls._plugin_classes = []
        else:
            cls._plugin_classes.append(cls)

class Plugin(object):
    __metaclass__ = PluginMetaClass

    def __init__(self, irc, *args, **kwargs):
        self.irc = irc

def _init_plugins(*args, **kwargs):
    """
    Create instances of the plugin classes and create a cache
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
                    _plugin_hooks[hook_key].append(
                            (attr.__module__, attr, hook_arg))

def load_plugins(plugindir, *args, **kwargs):
    global _plugins_module
    _plugins_module = __import__(plugindir)
    for p in dir(_plugins_module):
        if not p.startswith('_'):
            _plugins.append(p);
    _init_plugins(*args, **kwargs)

def reload_plugins(*args, **kwargs):
    if not _plugins_module:
        raise TypeError("load_plugins has never been called")
    _reset_variables()
    reload(_plugins_module)
    # When the modules are reloaded, the meta class will append
    # all of the classes again, so we need to make sure this is empty
    Plugin._plugin_classes = []
    for x in _plugins:
        reload(getattr(_plugins_module, x))
    # Add any new modules to _plugins
    for p in dir(_plugins_module):
        if not (p.startswith('_') or p in _plugins):
            _plugins.append(p);
    _init_plugins(*args, **kwargs)

def active_plugins():
    """
    Get the loaded plugin names
    """
    return _plugins

def active_plugin_classes():
    """
    Get the loaded plugin classes
    """
    return Plugin._plugin_classes

def get_command_doc(command):
    for _, cmd_hook, cmd in _plugin_hooks['command']:
        if cmd.upper() == command.upper():
            return cmd_hook.__doc__
    return "No command named '%s' found" % command
