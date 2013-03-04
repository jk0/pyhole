#   Copyright 2011 Johannes Erdfelt
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

"""Pyhole VersionOne Plugin"""

import traceback

from lxml import etree

from pyhole import plugin
from pyhole.plugins import projname
from pyhole.plugins import v1ircnick
from pyhole import utils

V1MAPPING = {'D':'Defect', 'E':'Epic', 'B':'Story', 'TK':'Task'}

class VersionOne(plugin.Plugin):
    """Provide access to the VersionOne API"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
        self.disabled = False
        self.projname = projname.Projname(irc)

        try:
            self.versionone = utils.get_config("VersionOne")
            self.versionone_domain = self.versionone.get("domain")
            self.versionone_key = self.versionone.get("key")
            self.versionone_username = self.versionone.get("username")
            self.versionone_password = self.versionone.get("password")
            self.versionone_baseurl = ("https://%s:%s@%s/") % (
                    self.versionone_username, self.versionone_password,
                    self.versionone_domain)
            self.versionone_url = ("https://%s:%s@%s/%s/VersionOne/"
                    "rest-1.v1") % (
                    self.versionone_username, self.versionone_password,
                    self.versionone_domain, self.versionone_key)
            self.v1ircnick = v1ircnick.V1ircnick(irc)

        except Exception:
            self.disabled = True

    @plugin.hook_add_keyword("d-")
    @utils.spawn
    def keyword_defect(self, params=None, **kwargs):
        """Retrieve VersionOne defect information (ex: D-01234)"""
        if params and not self.disabled:
            params = utils.ensure_int(params)
            if params:
                self._find_asset("Defect", "D-%s" % params)

    @plugin.hook_add_keyword("b-")
    @utils.spawn
    def keyword_backlog(self, params=None, **kwargs):
        """Retrieve VersionOne backlog information (ex: B-01234)"""
        if params and not self.disabled:
            params = utils.ensure_int(params)
            if params:
                self._find_asset("Story", "B-%s" % params)

    @plugin.hook_add_keyword("tk-")
    @utils.spawn
    def keyword_task(self, params=None, **kwargs):
        """Retrieve VersionOne task information (ex: TK-01234)"""
        if params and not self.disabled:
            params = utils.ensure_int(params)
            if params:
                self._find_asset("Task", "TK-%s" % params)

    @plugin.hook_add_keyword("g-")
    @utils.spawn
    def keyword_goal(self, params=None, **kwargs):
        """Retrieve VersionOne goal information (ex: G-01234)"""
        if params and not self.disabled:
            params = utils.ensure_int(params)
            if params:
                self._find_asset("Goal", "G-%s" % params)

    @plugin.hook_add_keyword("r-")
    @utils.spawn
    def keyword_request(self, params=None, **kwargs):
        """Retrieve VersionOne request information (ex: R-01234)"""
        if params and not self.disabled:
            params = utils.ensure_int(params)
            if params:
                self._find_asset("Request", "R-%s" % params)

    @plugin.hook_add_keyword("e-")
    @utils.spawn
    def keyword_epic(self, params=None, **kwargs):
        """Retrieve VersionOne epic information (ex: E-01234)"""
        if params and not self.disabled:
            params = utils.ensure_int(params)
            if params:
                self._find_asset("Epic", "E-%s" % params)

    @plugin.hook_add_keyword("i-")
    @utils.spawn
    def keyword_issue(self, params=None, **kwargs):
        """Retrieve VersionOne issue information (ex: I-01234)"""
        if params and not self.disabled:
            params = utils.ensure_int(params)
            if params:
                self._find_asset("Issue", "I-%s" % params)

    def _get_root_asset(self, type, number):
        """Find a VersionOne object"""
        url = "%s/Data/%s?where=Number='%s'" % (self.versionone_url,
                                                type, number)
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        try:
            return etree.XML(response.read())
        except Exception:
            traceback.print_exc()
            return


    def _find_asset(self, type, number):
        """Find and display a VersionOne object"""
        try:
            root = self._get_root_asset(type, number)
            asset = root.find("Asset")
            msg = self._format_asset_msg(type, asset)
            self.irc.reply(msg)
        except Exception:
            traceback.print_exc()
            return

    def _format_asset_msg(self, type, asset):
        type = self._get_type_for_code(type)

        id = asset.attrib['id']
        subject = asset.find('Attribute[@name="Name"]').text
        number = asset.find('Attribute[@name="Number"]').text
        status = asset.find('Attribute[@name="Status.Name"]')
        if status is not None:
            status = status.text
        owner = asset.find('Attribute[@name="Owners.Name"]/Value')
        if owner is not None:
            owner = owner.text

        msg = "V1 %s %s: %s" % (type, number, subject)

        attrs = []
        if status:
            attrs.append("Status: %s" % status)
        if type in ('Defect', 'Story'):
            attrs.append("Assignee: %s" % owner)

        if attrs:
            msg += " [%s]" % ", ".join(attrs)

        msg += self._get_link_to_asset(type, id)
        return msg

    def _get_link_to_asset(self, type, id):
        return" https://%s/%s/%s.mvc/Summary?oidToken=%s" % (
                self.versionone_domain, self.versionone_key,
                type, id)


    def _retrieve_asset_attributes(self, type, number, fieldlist):
        """Gets a v1 asset and returns the fields from fieldlist"""
        url = "%s/Data/%s?where=Number='%s'" % (self.versionone_url,
                                                type, number)

        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        try:
            root = etree.XML(response.read())
            asset = root.find("Asset")
            return [asset.attrib['id']] + [asset.find('Attribute[@name="%s"]' % field).text for field in fieldlist]
        except Exception:
            traceback.print_exc()
            return

    def _get_v1_member_id(self, username):
        """Gets a v1 asset and returns the fields from fieldlist"""
        url = "%s/Data/Member?where=Username='%s'" % (self.versionone_url, username)
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        try:
            root = etree.XML(response.read())
            asset = root.find("Asset")
            return asset.attrib['id']
        except Exception:
            traceback.print_exc()
            return

    def _assign_or_unassign_v1_asset(self, member_id, elem, act):
        url = self.versionone_baseurl + self._get_url_by_display_id(elem)

        root = etree.Element("Asset")
        owners = etree.Element("Relation", name="Owners")
	owner = etree.Element("Asset", idref=member_id, act=act)

        root.append(owners)
        owners.append(owner)

        # Post to the appropriate api
        data = etree.tostring(root)
        return self.irc.post_url(url, data)

    def _change_state(self, url, op):
        print self.versionone_url
        resp = self.irc.post_url(self.versionone_baseurl + url + "?op=" + op, "")
        for line in resp.readlines():
            print line

    @plugin.hook_add_command("v1close")
    @utils.spawn
    def v1close(self, params=None, **kwargs):
        """close stuff!"""
        if params:
            story = params.split(" ", 1)[0]
            self._change_state(self._get_url_by_display_id(story), "Inactivate")
        else:
            self.irc.reply(self.v1close.__doc__)

    @plugin.hook_add_command("v1open")
    @utils.spawn
    def v1open(self, params=None, **kwargs):
        """open stuff!"""
        if params:
            story = params.split(" ", 1)[0]
            self._change_state(self._get_url_by_display_id(story), "Reactivate")
        else:
            self.irc.reply(self.v1close.__doc__)

    def _parse_story_asset(self, asset, fieldlist):
        url = self._get_link_to_asset('Story', asset.attrib['id'].replace(':', '%3A'))
        return str([asset.find('Attribute[@name="%s"]' % field).text for field in fieldlist] + [url])


    @plugin.hook_add_command("liststories")
    @utils.spawn
    def v1liststories(self, params=None, **kwargs):
        status = ''
        try:
            project_id, status = params.split(" ", 1)
        except (AttributeError, ValueError):
            self.irc.reply("Usage: .liststories <project> <status>")

        if status == 'None':
            status = ''
        try:
            project_id = self.projname.get_project_id(project_id)
        except KeyError:
            pass


        url = "%s/Data/Story?where=Status.Name='%s';AssetState='64';Scope='Scope:%s'"
        url =  url % (self.versionone_url, status, project_id)

        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        try:
            root = etree.XML(response.read())
            assets = root.findall('Asset')
            to_print = ""
            for asset in assets:
                to_print += self._parse_story_asset(asset, ['Name']) + "\n"
        except Exception:
            traceback.print_exc()
            return

        self.irc.reply(str(to_print))

    @plugin.hook_add_command("v1asset")
    @utils.spawn
    def v1asset(self, params=None, **kwargs):
        """Create a V1 asset with optional description, syntax:
        .v1asset type project title[:description]"""
        if params:
            type, project, content = params.split(" ", 2)
            contents = content.split(":", 1)
            title = contents[0]
            desc = "TBD"
            if len(contents) > 1:
                desc = contents[1]
            try:
                project = self.projname.get_project_id(project)
            except KeyError:
                pass
            self._v1asset(type, project, title, desc)
        else:
            self.irc.reply(self.v1asset.__doc__)

    @plugin.hook_add_command("v1assign")
    @utils.spawn
    def v1assign(self, params=None, **kwargs):
        """Assign a asset to a IRC nick or V1 user, syntax:
        .v1assignnick [V1 story] [<nick/user> 
        .v1assignnick [V1 task] [<nick/user> 
        .v1assignnick [V1 epic] [<nick/user>]
        .v1assignnick [V1 issue] [<nick/user>]
        """
        if params:
            member_id, asset = self._parse_assign_unassign_params(params)
            self._assign_or_unassign_v1_asset(member_id, asset, "add")
            self.irc.reply("Assigned")
        else:
            self.irc.reply(self.v1assignstory.__doc__)

    @plugin.hook_add_command("v1unassign")
    @utils.spawn
    def v1unassign(self, params=None, **kwargs):
        """Unassign a IRC nick or V1 user from an asset, syntax:
        .v1unassignnick [V1 story] [<nick/user> 
        .v1unassignnick [V1 task] [<nick/user> 
        .v1unassignnick [V1 epic] [<nick/user>]
        .v1unassignnick [V1 issue] [<nick/user>]
        """
        if params:
            member_id, asset = self._parse_assign_unassign_params(params)
            self._assign_or_unassign_v1_asset(member_id, asset, "remove")
            self.irc.reply("Unassigned")
        else:
            self.irc.reply(self.v1assignstory.__doc__)

    def _parse_assign_unassign_params(self, params):
        """Helper method to parse the assign or assign methods"""
        data = params.split()
        asset = data[0]
        nick = data[1]
        username = self.v1ircnick.get_v1_username("show %s" % nick)
        if not username:
	    username = nick
        member_id = self._get_v1_member_id(username)
        return member_id, asset

    @plugin.hook_add_command("v1setstatus")
    @utils.spawn
    def v1setstatus(self, params=None, **kwargs):
        """Set the status of a story, syntax:
        .v1setstatus [<V1 story>] [status]"""
        if params:
            story, status = params.split(" ", 1)
            status_id = self._get_storystatus_id(status)
            self._update_story_status(status_id, story)
            self.irc.reply("status set")
        else:
            self.irc.reply(self.v1setstatus.__doc__)

    def _get_storystatus_id(self, status_name):
        url = "%s/Data/StoryStatus?where=Name='%s'" % (self.versionone_url, status_name)
        response = self.irc.fetch_url(url, self.name)
        assets = etree.XML(response.read())
        asset = assets.find('Asset')
        id = asset.attrib['id']
        return id

    def _update_story_status(self, status_id, story):
        url = self.versionone_baseurl + self._get_url_by_display_id(story)

        root = etree.Element("Asset")
        status = etree.Element("Relation", name="Status", act="set")
        storystatus = etree.Element("Asset", idref=status_id)

        root.append(status)
        status.append(storystatus)

        # Post to the appropriate api
        data = etree.tostring(root)
        return self.irc.post_url(url, data)

    def _v1asset(self, type, project, title, desc):
        response = self._create_asset(type, project, title, desc)
        # ugly hack to get the id
        asset = etree.XML(response.read())
        v1id = asset.attrib['id'].split(":")[1]
        v1display_num = self._get_display_id(type, v1id)
        self._find_asset(type, v1display_num)

    def _create_asset(self, type, project, title, description):
        """Create a new V1 asset (ex)
        example:
          <Asset>
          	<Attribute name="Name" act="set">TITLE</Attribute>
          	<Attribute name="Scope" act="set">Story:PROJECT</Attribute>
          	<Attribute name="Description" act="set">DESCRIPTION</Attribute>
          </Asset>
        """
        # Create the asset xml
        root = etree.Element("Asset")
        name = etree.Element("Attribute", name="Name", act="set")
        name.text = title
        scope = etree.Element("Attribute", name="Scope", act="set")
        scope.text = "Scope:%s" % project
        desc = etree.Element("Attribute", name="Description", act="set")
        desc.text = description

        root.append(name)
        root.append(scope)
        root.append(desc)

        # Post to the appropriate api
        url = "%s/Data/%s" % (self.versionone_url, type)
        data = etree.tostring(root)
        return self.irc.post_url(url, data)

    def _get_url_by_display_id(self, display_id):
        """"Gets the URL from the Display ID"""
        try:
            type = V1MAPPING[display_id[:display_id.index("-")]]
            assets = self._get_root_asset(type, display_id)
            return assets[0].get('href')
        except Exception:
            traceback.print_exc()
            return


    def _get_display_id(self, type, v1id):
        """Gets the Display ID from the actual v1 ID"""
        url = "%s/Data/%s/%s" % (self.versionone_url,
                                                type, v1id)
        response = self.irc.fetch_url(url, self.name)
        asset = etree.XML(response.read())
        return asset.find('Attribute[@name="Number"]').text

    def _update(self, type, v1id, attrname, attrtext):
        root = etree.Element("Asset")
        name = etree.Element("Attribute", name=attrname, act="set")
        name.text = attrtext
        root.append(name)

        url = "%s/Data/%s/%s" % (self.versionone_url, type, v1id)
        print url
        data = etree.tostring(root)
        print data
        return self.irc.post_url(url, data)

    def _create_link(self, name, url, link, onmenu=False):
        """Create a new V1 link (ex)
        example:
          <Asset>
                <Attribute name="URL" act="set">http://www.google.com</Attribute>
                <Attribute name="Name" act="set">test-api</Attribute>
                <Attribute name="OnMenu" act="set">false</Attribute>
                <Attribute name="Asset" act="set">Story:539391</Attribute>
          </Asset>
        """
        # Create the asset xml
        root = etree.Element("Asset")
        name_elt = etree.Element("Attribute", name="Name", act="set")
        name_elt.text = name
        url_elt = etree.Element("Attribute", name="URL", act="set")
        url_elt.text = url
        asset_link_elt = etree.Element("Attribute", name="Asset", act="set")
        asset_link_elt.text = link
        onmenu_elt = etree.Element("Attribute", name="OnMenu", act="set")
        onmenu_elt.text = str(onmenu)

        root.append(name_elt)
        root.append(url_elt)
        root.append(asset_link_elt)
        root.append(onmenu_elt)

        # Post to the appropriate api
        url = "%s/Data/Link" % self.versionone_url
        data = etree.tostring(root)
        return self.irc.post_url(url, data)

    def _filter_assets(self, type, sel=None, filters=None):
        type = self._get_type_for_code(type)

        url = "%s/Data/%s" % (self.versionone_url, type)

        queries = []

        if sel:
            queries.append("sel=%s" % sel)

        if filters:
            clauses = ["%s='%s'" % (key, value) for key, value in filters.iteritems()]
            queries.append("where=%s" % ";".join(clauses))

        if queries:
            query = "&".join(queries)
            url = "%s?%s" % (url, query)

        print "URL: %s" % url

        response = self.irc.fetch_url(url, self.name)
        assets = etree.XML(response.read())
        return assets

    def _get_type_for_code(self, type):
        if type in V1MAPPING:
            return V1MAPPING[type]
        else:
            return type

