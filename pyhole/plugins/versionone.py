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
from pyhole import utils


class VersionOne(plugin.Plugin):
    """Provide access to the VersionOne API"""

    def __init__(self, irc):
        self.irc = irc
        self.name = self.__class__.__name__
        self.disabled = False

        try:
            self.versionone = utils.get_config("VersionOne")
            self.versionone_domain = self.versionone.get("domain")
            self.versionone_key = self.versionone.get("key")
            self.versionone_username = self.versionone.get("username")
            self.versionone_password = self.versionone.get("password")
            self.versionone_url = ("https://%s:%s@%s/%s/VersionOne/"
                    "rest-1.v1") % (
                    self.versionone_username, self.versionone_password,
                    self.versionone_domain, self.versionone_key)
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

    def _find_asset(self, type, number):
        """Find and display a VersionOne object"""
        url = "%s/Data/%s?where=Number='%s'" % (self.versionone_url,
                                                type, number)
        print url
        response = self.irc.fetch_url(url, self.name)
        if not response:
            return

        try:
            #data = response.read()
            #import sys, xml.dom.minidom
            #print xml.dom.minidom.parseString(data).toprettyxml()
            #root = etree.XML(data)

            root = etree.XML(response.read())
            asset = root.find("Asset")
            id = asset.attrib['id']
            subject = asset.find('Attribute[@name="Name"]').text
            number = asset.find('Attribute[@name="Number"]').text
            status = asset.find('Attribute[@name="Status.Name"]')
            if status is not None:
                status = status.text
            owner = asset.find('Attribute[@name="Owners.Name"]/Value')
            if owner is not None:
                owner = owner.text
        except Exception:
            traceback.print_exc()
            return

        msg = "V1 %s #%s: %s" % (type, number, subject)

        attrs = []
        if status:
            attrs.append("Status: %s" % status)
        if type in ('Defect', 'Story'):
            attrs.append("Assignee: %s" % owner)

        if attrs:
            msg += " [%s]" % ", ".join(attrs)

        msg += " https://%s/%s/%s.mvc/Summary?oidToken=%s" % (
                self.versionone_domain, self.versionone_key,
                type, id)

        self.irc.reply(msg)
