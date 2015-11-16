#   Copyright 2015 Josh Kearney
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

"""Slack Client Class"""

import slackclient
import time

from pyhole.core import log
from pyhole.core import plugin
from pyhole.core import utils
from pyhole.core import version
from pyhole.core.slack import message


CONFIG = utils.get_config()
LOG = log.get_logger()


class Client(object):
    """A Slack Connection"""

    def __init__(self, network):
        log.setup_logger(str(network))
        self.network_config = utils.get_config(network)

        self.addressed = False
        self.client = None
        self.log = log.get_logger(str(network))
        self.version = version.version_string()

        self.admins = CONFIG.get("admins", type="list")
        self.command_prefix = CONFIG.get("command_prefix")

        self.api_token = self.network_config.get("api_token")
        self.nick = self.network_config.get("nick")

        self.load_plugins()

    def load_plugins(self, reload_plugins=False):
        """Load plugins and their commands respectively."""
        if reload_plugins:
            plugin.reload_plugins(session=self)
        else:
            plugin.load_plugins(session=self)

        self.log.info("Loaded Plugins: %s" % plugin.active_plugins())
        plugin.run_hook_polls(self)

    def start(self):
        """Run the Slack network connection."""
        self.client = slackclient.SlackClient(self.api_token)
        self.client.rtm_connect()

        while True:
            try:
                for response in self.client.rtm_read():
                    self.log.debug(response)

                    if all(x in response for x in ("text", "channel", "user")):
                        r_channel = response["channel"]
                        r_user = response["user"]

                        try:
                            channel = self.client.server.channels.find(
                                r_channel).name
                            user = self.client.server.users.find(r_user).name
                        except AttributeError:
                            continue

                        msg = response["text"]

                        self.log.info("-#%s- <%s> %s" % (channel, user, msg))

                        _msg = message.Reply(self, msg, user, channel)
                        plugin.poll_messages(self, _msg)

                time.sleep(.1)
            except Exception:
                # NOTE(jk0): Disconnected? Try to reconnect.
                self.client.rtm_connect()
                continue

    def reply(self, target, msg):
        """Reply to a channel."""
        channel = self.client.server.channels.find(target)
        channel.send_message(msg)

    def op_user(self, *args, **kwargs):
        pass

    def deop_user(self, *args, **kwargs):
        pass

    def set_nick(self, *args, **kwargs):
        pass

    def join_channel(self, *args, **kwargs):
        pass

    def part_channel(self, *args, **kwargs):
        pass

    def privmsg(self, *args, **kwargs):
        pass
