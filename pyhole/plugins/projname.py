#   Copyright 2013 Rackspace Hosting 
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

"""Pyhole Plugin to map VersionOne project id with name"""

import json

from pyhole import plugin
from pyhole import utils


class Projname(plugin.Plugin):
    """Set or display project name to project ID mappings syntax:
    .pn <sub_command> [project_name] [project_id]
    .pn set servers 502342
    .pn show servers
    .pn unset servers
    .pn list"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
        self.mapping_file = "projname"

    def get_project_id(self, name):
        data_file = utils.read_file(self.name, self.mapping_file)
        json_data = json.loads(data_file)
        project_id = json_data[name]
        return project_id
    
    @plugin.hook_add_command("projname")
    @utils.spawn
    def projname(self, params=None, **kwargs):
        mapping_file = self.mapping_file
        if params:
            sub_command = params
            if sub_command.startswith("set "):
                mapping = sub_command[4:].split()
                name = mapping[0]
                project_id = mapping[1]
                string_data = None

                #check if the mapping file exists
                if utils.check_file_exists(self.name, mapping_file):
                    data_file = utils.read_file(self.name, mapping_file)
                    json_data = json.loads(data_file)
                    json_data[name] = project_id
                    string_data = json.dumps(json_data)

                # if the file does not exist, create a new one and add the mapping
                else:
                    data = {}
                    data[name] = project_id
                    string_data = json.dumps(data)

                utils.write_file(self.name, mapping_file, string_data)
                self.irc.reply("name and Project ID association saved as %s <-> %s" % (name, project_id))

            elif sub_command.startswith("unset "):
                mapping = sub_command[6:].split()
                name = mapping[0]

                #check if the mapping file exists, else return with appropriate message
                if utils.check_file_exists(self.name, mapping_file):
                    data_file = utils.read_file(self.name, mapping_file)
                    json_data = json.loads(data_file)
                    project_id = json_data[name]
                    del json_data[name]
                    string_data = json.dumps(json_data)
                    utils.write_file(self.name, mapping_file, string_data)
                    self.irc.reply("name %s <-> Project ID %s association removed  %s <-> %s" % (name, project_id))

            elif sub_command.startswith("show "):
                mapping = sub_command[5:].split()
                name = mapping[0]

                #check if the mapping file exists, else return with appropriate message
                if not utils.check_file_exists(self.name, mapping_file):
                    self.irc.reply("There is no association with any project ID for the given name %s" % name)
                    return

                project_id = self.get_project_id(name) 
                self.irc.reply("%s <-> %s" % (name, project_id))

            elif sub_command.startswith("list"):
                if not utils.check_file_exists(self.name, mapping_file):
                    self.irc.reply("There are no associations for any name project ID")
                    return

                data_file = utils.read_file(self.name, mapping_file)
                json_data = json.loads(data_file)
                self.irc.reply("name <-> Project ID")
                for name, project_id in json_data.iteritems():
                    self.irc.reply("%s <-> %s" % (name, project_id))
            
            else:
                self.irc.reply("Usage .pn [<sub_command>] [<project_name>] [<project_id>]")
                return

    @plugin.hook_add_command("pn")
    def alias_w(self, params=None, **kwargs):
        """Alias of Projname"""
        self.projname(params, **kwargs)
