#   Copyright 2011 Paul Voccio
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

"""Pyhole Integration between bug tracking interfaces"""
import traceback

from lxml import etree

from launchpadlib.launchpad import Launchpad as LP

from pyhole import plugin
from pyhole import utils
from pyhole.plugins import versionone
from pyhole.plugins import launchpad
from pyhole.plugins import projname

class TrackingIntegration(plugin.Plugin):

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
        self.version_one = versionone.VersionOne(irc)
        self.launchpad = launchpad.Launchpad(irc)
	self.projname = projname.Projname(irc)

    @plugin.hook_add_command("importlp")
    @utils.spawn
    def importlp(self, params=None, **kwargs):
        """Import launchpad bug into V1 importlp <lpbugnumber> <v1project>"""
        if params:
            lpid, v1project = params.split(" ", 2)
            try:
                v1project = self.projname.get_project_id(v1project)
            except KeyError:
                pass
            bug = self.launchpad.launchpad.bugs[lpid]
            # We have info about the task now, lets import it into v1
            task = bug.bug_tasks[len(bug.bug_tasks) - 1]
            # Append the launchpad id
            desc = "<p>%s</p> <p>&nbsp;</p> <p>%s</p>" % (bug.description,
                                                          task.web_link)
            desc = desc.replace("\n","<br>")
            self.version_one._v1asset('Defect', v1project, bug.title, desc)
        else:
            self.irc.reply(self.importlp.__doc__)

    @plugin.hook_add_command("addreview")
    @utils.spawn
    def addreview(self, params=None, **kwargs):
        """Adds a gerrit review link to the V1 bug/story
           usage: addreview Defect|Story v1id gerritreview"""
        if params:
            v1id, gerritreview = params.split(" ", 2)
            typestr, v1id = v1id.split("-")
            type = versionone.V1MAPPING[typestr]
            # attrs always returns the v1id
            v1attrs = self.version_one._retrieve_asset_attributes(type,
                                                                  v1id,
                                                                  [])
            # Get the v1 oid in the form Defect:BLAH
            link = v1attrs[0]
            self.version_one._create_link("Review", gerritreview, link)
        else:
            self.irc.reply(self.addreview.__doc__)

    @plugin.hook_add_command("findreviews")
    @utils.spawn
    def findreviews(self, params=None, **kwargs):
        """Finds stories requiring reviews in the given project / scope
           usage: findreviews [B|D|E|TK] projectid
           where: B - backlog/stories, D - defects, E - epics, TK - tasks"""
        if params:
            p_list = params.split(" ", 1)
            if len(p_list) == 2:
                type = p_list[0].upper()

                project_id = None
                try:
                    project_id = self.projname.get_project_id(p_list[1])
                except KeyError:
                    project_id = p_list[1]

                if type in ['B','D','E','TK']:
                    self._find_reviews_for_asset_type(project_id, type)
                    return

        self.irc.reply(self.findreviews.__doc__)

    def _find_reviews_for_asset_type(self, project_id, asset_type):
        filters = {
            "Scope": ("Scope:%s" % project_id),
            "Links.Name": "Review",
            "AssetState": "64",
            }

        assets = self.version_one._filter_assets(asset_type, sel="Links,Name,Number,Status.Name,Owners.Name,Links.URL", filters=filters)
        found = False
        for elt in assets.iterchildren('Asset'):
            review_names = [value.text for value in elt.xpath("Attribute[@name='Links.Name']")[0].iterchildren('Value')]
            if "Review" in review_names:
                found = True
                review_links = [value.text for value in elt.xpath("Attribute[@name='Links.URL']")[0].iterchildren('Value')]
                self.irc.reply(self.version_one._format_asset_msg(asset_type, elt))
                for i in range(len(review_names)):
                    name = review_names[i]
                    if name == "Review":
                        self.irc.reply("%s: %s" % (name, review_links[i]))
        if not found:
            self.irc.reply("No items of type [%s] with reviews found" % asset_type)
