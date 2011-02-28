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

class PluginMetaClass(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, '_plugin_classes'):
            cls._plugin_classes = []
        else:
            cls._plugin_classes.append(cls)

class Plugin(object):
    __metaclass__ = PluginMetaClass

    _plugins = []
    _plugin_instances = []
    _keyword_hooks = []

    def __init__(self, *args, **kwargs):
        if 'irc' in kwargs:
            self.irc = kwargs['irc']

    @classmethod
    def _init_plugins(self, *args, **kwargs):
        for p in self._plugin_classes:
            # Create instance of 'p'
            instance = p(*args, **kwargs)
            # Store the instance
            self._plugin_instances.append(instance)

        # Setup _keyword_hooks
        for instance in self._plugin_instances:
            for attr_name in dir(instance):
                attr = getattr(instance, attr_name)
                if getattr(attr, '_is_keyword_hook', 0):
                    self._keyword_hooks.append(attr)

    @classmethod
    def load_plugins(self, plugindir, *args, **kwargs):
        self._plugins_module = __import__(plugindir)
        for p in dir(self._plugins_module):
            if not p.startswith('_'):
                self._plugins.append(p);
        self._init_plugins(*args, **kwargs)

    @classmethod
    def reload_plugins(self, *args, **kwargs):
        self._plugin_instances = []
        self._plugin_classes = []
        self._keyword_hooks = []
        reload(self._plugins_module)
        for x in self._plugins:
            reload(getattr(self._plugins_module, x))
        self._init_plugins(*args, **kwargs)

    @classmethod
    def plugins_loaded(self):
        for x in self._plugins:
            yield x

    @classmethod
    def plugin_classes_loaded(self):
        for x in self._plugin_classes:
            yield x

    @classmethod
    def keyword_hook(*args, **kwargs):
        def wrap(f):
            f._is_keyword_hook = 1
            f._keywords = args[1:]
            return f
        return wrap

    @classmethod
    def keyword_hooks(self):
        for kw_hook in self._keyword_hooks:
            yield kw_hook

