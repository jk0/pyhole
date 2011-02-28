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

import re

class PluginMetaClass(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, '_plugin_classes'):
            cls._plugin_classes = []
        else:
            cls._plugin_classes.append(cls)

class Plugin(object):
    __metaclass__ = PluginMetaClass

    _plugins = []

    @classmethod
    def _init_cls_vars(self):
        self._plugin_instances = []
        self._keyword_hooks = []
        self._message_hooks = []
        self._command_hooks = []

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
                if getattr(attr, '_is_keyword_hook', False):
                    self._keyword_hooks.append(attr)
                elif getattr(attr, '_is_command_hook', False):
                    self._command_hooks.append(attr)
                elif getattr(attr, '_is_message_hook', False):
                    self._message_hooks.append(attr)

    @classmethod
    def load_plugins(self, plugindir, *args, **kwargs):
        self._init_cls_vars()
        self._plugins_module = __import__(plugindir)
        for p in dir(self._plugins_module):
            if not p.startswith('_'):
                self._plugins.append(p);
        self._init_plugins(*args, **kwargs)

    @classmethod
    def reload_plugins(self, *args, **kwargs):
        self._init_cls_vars()
        self._plugin_classes = []
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
            f._is_keyword_hook = True
            f._regexp_matches = []
            f._keywords = args[1:]
            for arg in args[1:]:
                f._regexp_matches.append("(^|\s+)%s(\S+)" % arg)
            return f
        return wrap

    @classmethod
    def message_hook(*args, **kwargs):
        def wrap(f):
            f._is_message_hook = True
            f._regexp_matches = args[1:]
            return f
        return wrap

    @classmethod
    def command_hook(*args, **kwargs):
        def wrap(f):
            f._is_command_hook = 1
            f._commands = args[1:]
            return f
        return wrap

    @classmethod
    def keyword_hooks(self):
        for kw_hook in self._keyword_hooks:
            yield kw_hook

    @classmethod
    def active_keywords(self):
        keywords = []
        for kw_hook in self._keyword_hooks:
            keywords.extend(kw_hook._keywords)
        return keywords

    @classmethod
    def active_commands(self):
        commands = []
        for cmd_hook in self._command_hooks:
            commands.extend(cmd_hook._commands)
        return commands

    @classmethod
    def do_message_hook(self, message, private=False):

        for kw_hook in self._keyword_hooks:
            for kw_regexp in kw_hook._regexp_matches:
                m = re.search(kw_regexp, message, re.I)
                if m:
                    kw_hook(m.group(2), private=private,
                            full_message=message)

        for msg_hook in self._message_hooks:
            for msg_regexp in msg_hook._regexp_matches:
                m = re.search(msg_regexp, message, re.I)
                if m:
                    msg_hook(m, private=private, full_message=message)

    @classmethod
    def do_command_hook(self, command_prefix, nick, message, private=False):

        for cmd_hook in self._command_hooks:
            addressed=False

            if private:
                for cmd in cmd_hook._commands:
                    m = re.search("^%s$|^%s\s(.*)$" % (cmd, cmd),
                            message, re.I)
                    if m:
                        cmd_hook(m.group(1), command=cmd, 
                            private=private, addressed=addressed,
                            full_message=message)

            if message.startswith(command_prefix):
                # Strip off command prefix
                msg_rest = message[len(command_prefix):]
            else:
                # Check for command starting with nick being addressed
                msg_start_upper = message[:len(nick)+1].upper()
                if msg_start_upper == nick.upper() + ':':
                    # Get rest of string after "nick:" and white spaces
                    msg_rest = re.sub("^\s+", "", message[len(nick)+1:])
                else:
                    continue
                addressed=True

            for cmd in cmd_hook._commands:
                m = re.search("^%s$|^%s\s(.*)$" % (cmd, cmd),
                            msg_rest, re.I)
                if m:
                    cmd_hook(m.group(1), command=cmd, 
                            private=private, addressed=addressed,
                            full_message=message)
