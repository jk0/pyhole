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

import json

from pyhole import utils


def get_value(plugin_dir, mapping_file, key):
    data_file = utils.read_file(plugin_dir, mapping_file)
    json_data = json.loads(data_file)
    value = json_data[key]
    return value


def list_display(plugin_dir, mapping_file):
    #TODO: cleaner docstring
    """Lists out all the current mappings for key, value pairs"""
    if not utils.check_file_exists(plugin_dir, mapping_file):
        return None

    data_file = utils.read_file(plugin_dir, mapping_file)
    json_data = json.loads(data_file)
    return json_data.iteritems()


def show(plugin_dir, mapping_file, sub_command):
    """Shows the current mapping for a key with its value"""
    mapping = sub_command[5:].split()
    key = mapping[0]

    #check if the mapping file exists, else return with appropriate message
    if not utils.check_file_exists(plugin_dir, mapping_file):
        return key, None

    value = get_value(plugin_dir, mapping_file, key) 
    return key, value


def unassign(plugin_dir, mapping_file, sub_command):
    #TODO: cleaner docstring
    """Sets the mapping of key, value pair"""
    mapping = sub_command[6:].split()
    key = mapping[0]
    value = mapping[1]
    data = {}
    data[key] = value
	
    #check if the mapping file exists
    if utils.check_file_exists(plugin_dir, mapping_file):
        data_file = utils.read_file(plugin_dir, mapping_file)
        json_data = json.loads(data_file)
        del json_data[key]
        utils.write_file(plugin_dir, mapping_file, json.dumps(json_data))

    return key, value

def assign(plugin_dir, mapping_file, sub_command):
    #TODO: cleaner docstring
    """Sets the mapping of key, value pair"""
    mapping = sub_command[4:].split()
    key = mapping[0]
    value = mapping[1]
    data = {}
    data[key] = value
    json_data = json.dumps(data)
	
    #check if the mapping file exists
    if utils.check_file_exists(plugin_dir, mapping_file):
        data_file = utils.read_file(plugin_dir, mapping_file)
        json_data = json.loads(data_file)
        json_data[key] = value
        utils.write_file(plugin_dir, mapping_file, json.dumps(json_data))

    else:
        # if the file does not exist, create a new one and add the mapping
        utils.write_file(plugin_dir, mapping_file, json_data)

    return key, value
